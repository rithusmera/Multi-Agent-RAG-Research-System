import json
import logging
import re
from typing import Dict, Any

from agents.llm import llm, get_llm_response_text

logger = logging.getLogger(__name__)

def evaluator(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluator Agent node in LangGraph.
    Evaluates answer quality and completeness of gathered RAG & Web research results against the user query.
    Determines if information is sufficient to proceed to Response Agent or requires another research pass.
    """
    query = state.get("query", "")
    rag_results = state.get("rag_results", [])
    research_results = state.get("research_results", [])
    iteration_count = state.get("iteration_count", 0) + 1

    # Formulate context summary for LLM evaluation
    rag_summary = "\n".join([f"- [{doc.get('title')}] {doc.get('content')}" for doc in rag_results]) or "None"
    research_summary = "\n".join([f"- [{res.get('title')}] {res.get('content')}" for res in research_results]) or "None"

    prompt = f"""
    You are an expert Evaluator Agent in a Multi-Agent Research System.

    User Query:
    "{query}"

    Gathered Context from Internal Knowledge Base (RAG):
    {rag_summary}

    Gathered Context from External Web Research:
    {research_summary}

    Current Iteration: {iteration_count}

    Assess whether the gathered context is sufficient and detailed enough to fully answer the user query accurately.

    Return ONLY a JSON object formatted as follows:
    {{
        "is_sufficient": true/false,
        "score": <numeric score 0 to 100>,
        "feedback": "<detailed assessment explanation>",
        "missing_information": "<specific missing topics or questions if insufficient, otherwise empty>"
    }}
    """

    try:
        response = llm.invoke(prompt)
        text_response = get_llm_response_text(response)
        
        # Parse JSON output from LLM
        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if json_match:
            eval_data = json.loads(json_match.group(0))
        else:
            eval_data = json.loads(text_response)
            
        is_sufficient = bool(eval_data.get("is_sufficient", True))
        score = float(eval_data.get("score", 85.0))
        feedback = str(eval_data.get("feedback", "Gathered content appears sufficient."))
        missing_info = str(eval_data.get("missing_information", ""))
    except Exception as e:
        logger.warning(f"[Evaluator Agent] Parsing error: {e}. Falling back to default evaluation.")
        # Fallback check
        has_content = bool(rag_results or research_results)
        is_sufficient = has_content
        score = 80.0 if has_content else 40.0
        feedback = "Evaluated gathered findings." if has_content else "No context retrieved yet."
        missing_info = "" if has_content else "Need initial topic research."

    evaluation_result = {
        "is_sufficient": is_sufficient,
        "score": score,
        "feedback": feedback,
        "missing_information": missing_info
    }

    logger.info(f"[Evaluator Agent] Iteration {iteration_count} | Sufficient: {is_sufficient} | Score: {score}")

    messages = state.get("messages", [])
    if not isinstance(messages, list):
        messages = []

    status_str = "Sufficient" if is_sufficient else "Insufficient"
    messages.append({
        "agent": "Evaluator Agent",
        "message": f"Evaluation Score: {score}/100 ({status_str}). Feedback: {feedback}"
    })

    return {
        "evaluation": evaluation_result,
        "iteration_count": iteration_count,
        "messages": messages
    }