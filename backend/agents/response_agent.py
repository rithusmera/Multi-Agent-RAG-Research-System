import logging
from typing import Dict, Any

from agents.llm import llm, get_llm_response_text

logger = logging.getLogger(__name__)

def response_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Response Agent node in LangGraph.
    Synthesizes all gathered RAG context, web research findings, evaluation context,
    and human feedback into a comprehensive, formatted research response with citations.
    """
    query = state.get("query", "")
    rag_results = state.get("rag_results", [])
    research_results = state.get("research_results", [])
    evaluation = state.get("evaluation", {})
    human_feedback = state.get("human_feedback", "")
    iteration_count = state.get("iteration_count", 0)

    # Prepare evidence formatting
    rag_formatted = ""
    for idx, doc in enumerate(rag_results, 1):
        rag_formatted += f"[{idx}] {doc.get('title')} ({doc.get('source')})\nContent: {doc.get('content')}\n\n"
    if not rag_formatted:
        rag_formatted = "No internal knowledge base records retrieved."

    research_formatted = ""
    for idx, res in enumerate(research_results, 1):
        research_formatted += f"[{idx}] {res.get('title')} ({res.get('source')})\nContent: {res.get('content')}\n\n"
    if not research_formatted:
        research_formatted = "No external web research findings retrieved."

    prompt = f"""
    You are the Response Agent of an advanced Multi-Agent Research System.
    Synthesize a clear, authoritative, and comprehensive final research report addressing the user query.

    User Query:
    "{query}"

    Internal Knowledge Base Context:
    {rag_formatted}

    External Web Research Findings:
    {research_formatted}

    Quality Evaluation Score: {evaluation.get('score', 85)}/100
    Evaluator Feedback: {evaluation.get('feedback', 'Sufficient')}
    Human Steering Feedback (if any): {human_feedback or 'None'}

    Format your response in Markdown with clear sections:
    # Executive Summary
    # Detailed Analysis & Findings
    # Key System & Technical Insights
    # References & Source Citations
    """

    try:
        response = llm.invoke(prompt)
        final_answer = get_llm_response_text(response)
    except Exception as e:
        logger.error(f"[Response Agent] Synthesis LLM error: {e}. Generating fallback summary.")
        final_answer = f"""# Research Response

## Query
{query}

## Summary of Findings
Based on internal knowledge base search ({len(rag_results)} docs) and web research ({len(research_results)} items):

### Knowledge Base Highlights:
{rag_formatted}

### Web Research Highlights:
{research_formatted}

*Evaluation Score: {evaluation.get('score', 80)}/100 across {iteration_count} iteration(s).*
"""

    messages = state.get("messages", [])
    if not isinstance(messages, list):
        messages = []

    messages.append({
        "agent": "Response Agent",
        "message": "Generated final synthesized research response."
    })

    logger.info("[Response Agent] Successfully generated final answer report.")

    return {
        "final_answer": final_answer,
        "messages": messages,
        "next_agent": "END"
    }