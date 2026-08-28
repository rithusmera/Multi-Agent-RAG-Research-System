import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def human_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Human-in-the-loop (HITL) node in LangGraph.
    Provides a checkpoint pause/resume point where human feedback, approval,
    or steering instructions can be injected into the research workflow state.
    """
    human_feedback = state.get("human_feedback", None)
    evaluation = state.get("evaluation", {})
    iteration_count = state.get("iteration_count", 0)

    logger.info(f"[Human-in-the-Loop Node] Checkpoint activated. Feedback present: {bool(human_feedback)}")

    messages = state.get("messages", [])
    if not isinstance(messages, list):
        messages = []

    if human_feedback:
        messages.append({
            "agent": "Human Reviewer",
            "message": f"Human feedback injected: '{human_feedback}'. Requesting workflow continuation."
        })
        # If feedback provided, hand back to supervisor to refine research
        return {
            "human_approved": False,
            "next_agent": "supervisor",
            "messages": messages
        }
    else:
        messages.append({
            "agent": "Human Reviewer",
            "message": "Human review completed: Approved proceeding to final response generation."
        })
        return {
            "human_approved": True,
            "next_agent": "response",
            "messages": messages
        }
