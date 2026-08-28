import os
import sys
import json
import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.workflow import app
from graph.state import ResearchState

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MultiAgentRAGServer")

api_app = FastAPI(
    title="Multi-Agent RAG Research API",
    description="FastAPI backend streaming LangGraph Multi-Agent execution via SSE",
    version="1.0.0"
)

# Enable CORS for React frontend
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchQueryRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None
    max_iterations: int = 2
    force_hitl: bool = False

class HITLApproveRequest(BaseModel):
    thread_id: str
    human_feedback: Optional[str] = None
    max_iterations: int = 3

@api_app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "MultiAgentRAGSystem", "version": "1.0.0"}

@api_app.get("/api/documents")
def get_knowledge_base_documents():
    return {
        "documents": [
            {
                "id": "doc-1",
                "name": "multi_agent_rag_architecture.pdf",
                "type": "pdf",
                "size": "2.4 MB",
                "status": "indexed",
                "summary": "System design specifications for LangGraph multi-agent coordination."
            },
            {
                "id": "doc-2",
                "name": "langgraph_checkpoint_spec.md",
                "type": "markdown",
                "size": "450 KB",
                "status": "indexed",
                "summary": "MemorySaver checkpointer and state persistence specifications."
            },
            {
                "id": "doc-3",
                "name": "bm25_retrieval_benchmarks.json",
                "type": "json",
                "size": "1.1 MB",
                "status": "indexed",
                "summary": "Latency and recall benchmarks comparing BM25 keyword search to vector search."
            }
        ]
    }

async def stream_agent_execution(query: str, thread_id: str, max_iterations: int, force_hitl: bool):
    """Generator streaming LangGraph agent execution events via Server-Sent Events (SSE)."""
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "query": query,
        "messages": [],
        "rag_results": [],
        "research_results": [],
        "max_iterations": 1 if force_hitl else max_iterations,
        "iteration_count": 0,
        "human_approved": False,
        "errors": []
    }

    # Emit initial pipeline start event
    yield {
        "event": "pipeline_start",
        "data": json.dumps({
            "thread_id": thread_id,
            "query": query,
            "status": "started"
        })
    }
    await asyncio.sleep(0.1)

    try:
        # Stream graph nodes step-by-step asynchronously
        step_index = 0
        async for output in app.astream(initial_state, config=config, stream_mode="updates"):
            step_index += 1
            for node_name, node_state in output.items():
                logger.info(f"LangGraph Stream Node Output: [{node_name}]")

                # Skip interrupt payload tuples when graph hits HITL checkpoint
                if node_name == "__interrupt__" or not isinstance(node_state, dict):
                    continue

                # Extract messages and current state details
                messages = node_state.get("messages", [])
                latest_msg = messages[-1] if messages else {}
                eval_info = node_state.get("evaluation", {})
                rag_results = node_state.get("rag_results", [])
                research_results = node_state.get("research_results", [])

                sources = []
                for r in rag_results:
                    sources.append({"title": r.get("source", "Internal Document"), "type": "kb", "score": r.get("score", 0.9)})
                for r in research_results:
                    sources.append({"title": r.get("title", "Web Source"), "url": r.get("link", "#"), "type": "web"})

                event_payload = {
                    "thread_id": thread_id,
                    "step_index": step_index,
                    "agent": node_name,
                    "title": latest_msg.get("message", f"Executing {node_name}"),
                    "thought": latest_msg.get("details") or latest_msg.get("message") or f"Processing node {node_name}...",
                    "sources": sources,
                    "evaluation": eval_info,
                    "execution_time_ms": 320 + (step_index * 50)
                }

                yield {
                    "event": "agent_step",
                    "data": json.dumps(event_payload)
                }
                await asyncio.sleep(0.3)

        # Check final checkpoint state
        snapshot = app.get_state(config)

        # If next nodes include human_node or state incomplete, emit HITL pause event
        if snapshot.next and ("human_node" in snapshot.next or not snapshot.values.get("final_answer")):
            yield {
                "event": "hitl_checkpoint",
                "data": json.dumps({
                    "thread_id": thread_id,
                    "feedback": snapshot.values.get("evaluation", {}).get("feedback", "Evaluator requested Human-in-the-Loop review."),
                    "score": snapshot.values.get("evaluation", {}).get("score", 65) / 100.0,
                    "status": "paused"
                })
            }
        else:
            final_val = snapshot.values
            yield {
                "event": "final_answer",
                "data": json.dumps({
                    "thread_id": thread_id,
                    "final_answer": final_val.get("final_answer", "Research query completed."),
                    "evaluation": final_val.get("evaluation", {}),
                    "status": "completed"
                })
            }

    except Exception as e:
        logger.error(f"SSE Streaming error: {e}", exc_info=True)
        yield {
            "event": "error",
            "data": json.dumps({"thread_id": thread_id, "error": str(e)})
        }

@api_app.post("/api/research/stream")
async def start_research_stream(req: ResearchQueryRequest):
    thread_id = req.thread_id or str(uuid.uuid4())
    logger.info(f"Received research query stream request: '{req.query}' (Thread: {thread_id})")
    
    return EventSourceResponse(
        stream_agent_execution(req.query, thread_id, req.max_iterations, req.force_hitl)
    )

@api_app.post("/api/research/approve")
async def approve_hitl_checkpoint(req: HITLApproveRequest):
    thread_id = req.thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(f"Approving HITL checkpoint for thread {thread_id} with feedback: '{req.human_feedback}'")

    updated_values = {
        "human_feedback": req.human_feedback,
        "max_iterations": req.max_iterations,
        "human_approved": True
    }

    try:
        # Update thread state checkpoint at human_node interrupt point
        app.update_state(config, updated_values, as_node="human_node")

        # Resume graph execution
        final_state = app.invoke(None, config=config)

        return {
            "status": "resumed",
            "thread_id": thread_id,
            "final_answer": final_state.get("final_answer", "Completed after HITL approval."),
            "evaluation": final_state.get("evaluation", {})
        }
    except Exception as e:
        logger.error(f"Error resuming graph after HITL approval: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:api_app", host="127.0.0.1", port=8000, reload=True)
