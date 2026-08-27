from typing import TypedDict

class ResearchState(TypedDict):
    query: str

    next_agent: str

    rag_results: list
    research_results: list

    evaluation: dict

    final_answer: str
