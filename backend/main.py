import sys
import uuid
import logging
from typing import Dict, Any

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from graph.workflow import app


# Configure clean logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MultiAgentRAGSystem")

def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def run_research_query(query: str, thread_id: str = None, max_iterations: int = 2, human_feedback: str = None) -> Dict[str, Any]:
    """Execute a query through the Multi-Agent LangGraph System with checkpointing."""
    if not thread_id:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "query": query,
        "messages": [],
        "rag_results": [],
        "research_results": [],
        "max_iterations": max_iterations,
        "iteration_count": 0,
        "human_feedback": human_feedback,
        "human_approved": False,
        "errors": []
    }

    print_header(f"Multi-Agent Research System | Thread ID: {thread_id[:8]}")
    print(f"User Query: {query}")
    if human_feedback:
        print(f"Human Steering Feedback: {human_feedback}")
    print("-" * 80)

    try:
        # Invoke compiled graph with memory checkpointing
        final_state = app.invoke(initial_state, config=config)

        print_header("Agent Execution Handoff Log")
        for msg in final_state.get("messages", []):
            agent_name = msg.get("agent", "System")
            text = msg.get("message", "")
            print(f"-> [{agent_name}] {text}")


        print_header("Final Research Report")
        final_answer = final_state.get("final_answer", "No answer generated.")
        print(final_answer)

        eval_info = final_state.get("evaluation", {})
        print_header("Evaluation & Performance Metrics")
        print(f"• Overall Quality Score: {eval_info.get('score', 'N/A')}/100")
        print(f"• Sufficiency Check: {eval_info.get('is_sufficient', 'N/A')}")
        print(f"• Evaluator Feedback: {eval_info.get('feedback', 'N/A')}")
        print(f"• Total Evaluator Iterations: {final_state.get('iteration_count', 0)}")
        print(f"• RAG Sources Used: {len(final_state.get('rag_results', []))}")
        print(f"• Web Research Sources Used: {len(final_state.get('research_results', []))}")

        return final_state
    except Exception as e:
        logger.error(f"Execution error running graph: {e}", exc_info=True)
        return {"error": str(e)}

def run_human_in_the_loop_demo():
    """Demonstrate Human-in-the-Loop (HITL) workflow & state persistence using LangGraph checkpointing."""
    print_header("Human-in-the-Loop (HITL) Workflow Demonstration")
    thread_id = f"hitl-demo-{uuid.uuid4().hex[:6]}"
    query = "Compare LangGraph state machine features with custom LLM agent loops."

    print(f"Step 1: Launching initial agent workflow (Thread: {thread_id})...")
    config = {"configurable": {"thread_id": thread_id}}
    
    # Run initial pass with low max_iterations to force HITL checkpoint pause
    initial_state = {
        "query": query,
        "messages": [],
        "rag_results": [],
        "research_results": [],
        "max_iterations": 1, # force human node after 1 iteration
        "iteration_count": 0,
        "human_approved": False
    }

    step1_state = app.invoke(initial_state, config=config)

    print("\n[HITL Checkpoint Reached] System paused for Human Review!")
    current_snapshot = app.get_state(config)
    print(f"Saved Checkpoint Next Nodes: {current_snapshot.next}")
    print(f"Current Evaluation Score: {step1_state.get('evaluation', {}).get('score', 'N/A')}")

    # Simulate Human Feedback injection into saved state checkpoint
    human_input = "Please focus specifically on checkpoint persistence, time travel, and memory savers."
    print(f"\nStep 2: Human injects feedback: '{human_input}'...")

    updated_state = {
        "human_feedback": human_input,
        "max_iterations": 3 # extend limit for refined run
    }

    # Resume graph execution from thread checkpoint
    app.update_state(config, updated_state)
    print("\nStep 3: Resuming workflow from thread checkpoint...")
    final_hitl_state = app.invoke(None, config=config)

    print_header("HITL Final Synthesized Result")
    print(final_hitl_state.get("final_answer", ""))
    return final_hitl_state

def main():
    """CLI Runner entrypoint."""
    if len(sys.argv) > 1:
        query_arg = " ".join(sys.argv[1:])
        if query_arg.lower() == "--hitl":
            run_human_in_the_loop_demo()
        else:
            run_research_query(query_arg)
    else:
        # Default run query demonstrating full Multi-Agent RAG workflow
        default_query = "What is Retrieval-Augmented Generation (RAG) and how do Multi-Agent frameworks like LangGraph enhance it?"
        run_research_query(default_query)

if __name__ == "__main__":
    main()