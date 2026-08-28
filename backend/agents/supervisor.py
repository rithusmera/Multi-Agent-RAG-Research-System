import logging
from typing import Dict, Any

from agents.llm import llm, get_llm_response_text

logger = logging.getLogger(__name__)

def supervisor(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Supervisor Agent node in LangGraph.
    Coordinates workflow execution by determining which specialized agent should process next.
    Routes dynamically between 'rag', 'research', 'both', 'human', or 'response'.
    """
    query = state.get("query", "")
    rag_results = state.get("rag_results", [])
    research_results = state.get("research_results", [])
    evaluation = state.get("evaluation", {})
    iteration_count = state.get("iteration_count", 0)
    human_feedback = state.get("human_feedback", None)

    # Check if coming back from Evaluator with feedback
    missing_info = evaluation.get("missing_information", "") if isinstance(evaluation, dict) else ""
    is_sufficient = evaluation.get("is_sufficient", False) if isinstance(evaluation, dict) else False

    # If human feedback is present, integrate human guidance into query strategy
    if human_feedback:
        logger.info(f"[Supervisor Agent] Processing with Human Feedback: {human_feedback}")

    prompt = f"""
    You are the Supervisor Agent of a Multi-Agent Research System.
    Your role is to orchestrate control flow between specialized research agents.

    User Query:
    "{query}"

    Status Summary:
    - RAG Results Gathered: {len(rag_results)} document(s)
    - Web Research Results Gathered: {len(research_results)} item(s)
    - Iteration Count: {iteration_count}
    - Last Evaluator Feedback: {evaluation.get('feedback', 'None')}
    - Missing Information Identified: {missing_info or 'None'}
    - Human Steering Feedback: {human_feedback or 'None'}

    Available Next Routing Choices:
    1. "rag" - Use Internal Knowledge Base retriever (best for architecture, core system design, internal RAG docs)
    2. "research" - Use external web search (best for recent news, external APIs, broad web facts)
    3. "both" - Trigger both RAG and Research sequentially
    4. "response" - Generate final synthesized response (use if sufficient or max retries reached)

    Return ONLY one word representing your decision:
    rag
    OR
    research
    OR
    both
    OR
    response
    """

    try:
        response = llm.invoke(prompt)
        content = get_llm_response_text(response).lower().strip()
        
        if "rag" in content:
            next_agent = "rag"
        elif "research" in content:
            next_agent = "research"
        elif "both" in content:
            next_agent = "both"
        elif "response" in content:
            next_agent = "response"
        else:
            # Fallback logic based on current results state
            if not rag_results:
                next_agent = "rag"
            elif not research_results:
                next_agent = "research"
            else:
                next_agent = "response"
    except Exception as e:
        logger.error(f"[Supervisor Agent] Decision LLM error: {e}. Defaulting to 'rag'.")
        next_agent = "rag" if not rag_results else "research"

    logger.info(f"[Supervisor Agent] Routing decision -> '{next_agent}'")

    messages = state.get("messages", [])
    if not isinstance(messages, list):
        messages = []

    messages.append({
        "agent": "Supervisor Agent",
        "message": f"Orchestration decision: Handoff to '{next_agent}' agent (Iteration {iteration_count})."
    })

    return {
        "next_agent": next_agent,
        "messages": messages
    }