import json
import re
import logging
from typing import Dict, Any

from agents.llm import llm, get_llm_response_text

logger = logging.getLogger(__name__)

def supervisor(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Supervisor Agent node in LangGraph.
    Coordinates workflow execution by determining which specialized agent should process next,
    and generates an optimized short search query distilled from the user request or missing context.
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

    # If human feedback is present, integrate human guidance into query strategy
    if human_feedback:
        logger.info(f"[Supervisor Agent] Processing with Human Feedback: {human_feedback}")

    prompt = f"""
    You are the Supervisor Agent of a Multi-Agent Research System.
    Your role is to orchestrate control flow between specialized research agents and generate a concise, high-precision search query.

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

    Return ONLY a JSON object formatted as follows:
    {{
        "next_agent": "rag" | "research" | "both" | "response",
        "search_query": "<concise 3-7 word keyword search query optimized for search engines/retrieval>"
    }}
    """

    next_agent = "rag"
    search_query = query.split('?')[0].split('.')[0].strip() if ('?' in query or '.' in query) else query[:80]

    try:
        response = llm.invoke(prompt)
        content = get_llm_response_text(response)
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
        else:
            data = json.loads(content)

        raw_agent = str(data.get("next_agent", "rag")).lower().strip()
        if "rag" in raw_agent:
            next_agent = "rag"
        elif "research" in raw_agent:
            next_agent = "research"
        elif "both" in raw_agent:
            next_agent = "both"
        elif "response" in raw_agent:
            next_agent = "response"

        if data.get("search_query"):
            search_query = str(data["search_query"]).strip()

    except Exception as e:
        logger.warning(f"[Supervisor Agent] JSON parse or LLM error: {e}. Utilizing fallback query.")
        content_lower = str(response.content if hasattr(response, 'content') else str(response)).lower() if 'response' in locals() else ""
        if "research" in content_lower:
            next_agent = "research"
        elif "response" in content_lower:
            next_agent = "response"
        else:
            next_agent = "rag" if not rag_results else "research"

    logger.info(f"[Supervisor Agent] Routing decision -> '{next_agent}' | Generated Search Query -> '{search_query}'")

    messages = state.get("messages", [])
    if not isinstance(messages, list):
        messages = []

    messages.append({
        "agent": "Supervisor Agent",
        "message": f"Orchestration decision: Handoff to '{next_agent}' agent (Query: '{search_query}')."
    })

    return {
        "next_agent": next_agent,
        "search_query": search_query,
        "messages": messages
    }