import logging
import math
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Pre-seeded Internal Knowledge Base Documents
KNOWLEDGE_BASE_DOCS = [
    {
        "id": "kb-001",
        "title": "RAG (Retrieval-Augmented Generation) Architecture Overview",
        "content": (
            "Retrieval-Augmented Generation (RAG) is a pattern that combines Information Retrieval (IR) "
            "with Large Language Models (LLMs). The core components of a RAG system are: "
            "1. Document Ingestion & Chunking (Recursive, Character, Semantic). "
            "2. Vector Embedding Generation (Dense representation of text semantics). "
            "3. Vector Database Storage (FAISS, Chroma, Pinecone, Qdrant). "
            "4. Semantic Similarity Search (Cosine similarity, Dot product, Euclidean distance). "
            "5. Context Injection into Prompt: The retrieved top-k context passages are concatenated into "
            "the LLM prompt to reduce hallucination and provide up-to-date domain specific knowledge."
        ),
        "tags": ["rag", "architecture", "retrieval", "embeddings", "vector_db"]
    },
    {
        "id": "kb-002",
        "title": "LangGraph & Multi-Agent Orchestration Patterns",
        "content": (
            "LangGraph is a framework for building stateful, multi-actor applications with LLMs using graph structures. "
            "Key patterns include: "
            "1. Supervisor Pattern: A central coordinator agent dynamically routes control to specialized sub-agents based on "
            "state analysis. "
            "2. Shared State Graph: All agents read from and mutate a centralized TypedDict state schema. "
            "3. Conditional Edges & Handoffs: Dynamic routing based on agent completion status or evaluator quality checks. "
            "4. Checkpointing & Persistence: Saving graph state snapshots using MemorySaver or SqliteSaver to enable human-in-the-loop "
            "approval, time travel, and crash recovery."
        ),
        "tags": ["langgraph", "multi-agent", "supervisor", "state", "checkpointing"]
    },
    {
        "id": "kb-003",
        "title": "Evaluator-Optimizer & Feedback Loop Design",
        "content": (
            "In multi-agent systems, the Evaluator Agent plays a crucial quality assurance role. "
            "It assesses whether the retrieved research or generated answer meets completeness, correctness, and relevance criteria. "
            "If the evaluation score is below threshold (or marked insufficient), the Evaluator formulates targeted feedback "
            "and routes back to the Supervisor Agent. The Supervisor then triggers missing research topics or secondary queries. "
            "To prevent infinite loops, an iteration_count cap is enforced before escalating to Human-in-the-loop intervention."
        ),
        "tags": ["evaluator", "feedback_loop", "quality", "supervisor", "retry"]
    },
    {
        "id": "kb-004",
        "title": "Human-in-the-Loop (HITL) and Checkpointing Strategies",
        "content": (
            "Human-in-the-loop capability allows human reviewers to inspect, edit, or steer agent workflows. "
            "In LangGraph, this is achieved by using thread checkpointing (`interrupt_before` or explicit review nodes). "
            "When triggered, graph execution pauses at a specific checkpoint. A human can provide feedback, override decision flags, "
            "or update state variables before resuming graph execution from the exact saved state."
        ),
        "tags": ["human_in_the_loop", "hitl", "checkpointing", "interrupt", "memory_saver"]
    },
    {
        "id": "kb-005",
        "title": "Vector Embeddings, Hybrid Search & Chunking",
        "content": (
            "Effective RAG systems leverage hybrid search combining sparse lexical retrieval (BM25, TF-IDF) with "
            "dense vector retrieval (embeddings). Chunking strategies involve setting chunk sizes (e.g. 512-1024 tokens) "
            "and overlap (e.g. 10-20%) to maintain local narrative context. Reciprocal Rank Fusion (RRF) is often used to merge "
            "sparse and dense search result rankings for maximum recall."
        ),
        "tags": ["search", "hybrid", "bm25", "embeddings", "chunking", "vector_db"]
    }
]

def _tokenize(text: str) -> List[str]:
    """Basic word tokenization for similarity scoring."""
    return re.findall(r'\w+', text.lower())

def search_internal_kb(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search internal knowledge base using keyword frequency & BM25-style term matching."""
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return KNOWLEDGE_BASE_DOCS[:top_k]

    scored_docs = []
    for doc in KNOWLEDGE_BASE_DOCS:
        doc_tokens = _tokenize(doc["title"] + " " + doc["content"] + " " + " ".join(doc["tags"]))
        match_count = sum(1 for token in query_tokens if token in doc_tokens)
        
        # Calculate term overlap ratio
        score = match_count / max(1, len(query_tokens))
        
        # Give bonus for tag matches
        for tag in doc["tags"]:
            if tag in query_tokens:
                score += 0.5

        scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    
    results = []
    for score, doc in scored_docs[:top_k]:
        results.append({
            "source": f"Internal KB: {doc['title']} ({doc['id']})",
            "title": doc["title"],
            "content": doc["content"],
            "relevance_score": round(score, 2),
            "type": "internal_kb"
        })
    return results

def rag_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    RAG Agent node in LangGraph.
    Searches the internal knowledge base for information relevant to the user query and evaluator feedback.
    """
    query = state.get("query", "")
    evaluation = state.get("evaluation", {})
    missing_info = evaluation.get("missing_information", "") if isinstance(evaluation, dict) else ""
    
    search_query = query
    if missing_info and len(missing_info.strip()) > 0:
        search_query += f" {missing_info}"

    logger.info(f"[RAG Agent] Searching Internal Knowledge Base for query: '{search_query}'")

    try:
        retrieved_docs = search_internal_kb(search_query, top_k=2)
    except Exception as e:
        logger.error(f"[RAG Agent] Error searching KB: {e}")
        retrieved_docs = [{
            "source": "Internal KB Error Fallback",
            "title": "Knowledge Base Search Exception",
            "content": f"Failed to query knowledge base: {str(e)}",
            "relevance_score": 0.0,
            "type": "internal_kb"
        }]

    existing_rag = state.get("rag_results", [])
    if not isinstance(existing_rag, list):
        existing_rag = []
    
    updated_rag = existing_rag + retrieved_docs

    messages = state.get("messages", [])
    if not isinstance(messages, list):
        messages = []
        
    messages.append({
        "agent": "RAG Agent",
        "message": f"Retrieved {len(retrieved_docs)} relevant context document(s) from Internal Knowledge Base."
    })

    return {
        "rag_results": updated_rag,
        "messages": messages,
        "next_agent": "evaluator"
    }