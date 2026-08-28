from typing import TypedDict, List, Dict, Any, Optional

class ResearchState(TypedDict, total=False):
    query: str
    search_query: Optional[str]
    messages: List[Dict[str, Any]]
    next_agent: str
    rag_results: List[Dict[str, Any]]
    research_results: List[Dict[str, Any]]
    evaluation: Dict[str, Any]
    iteration_count: int
    max_iterations: int
    human_feedback: Optional[str]
    human_approved: bool
    final_answer: str
    errors: List[str]

