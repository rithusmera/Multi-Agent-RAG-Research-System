from agents.llm import llm

def supervisor(state):
    query = state['query']

    prompt = f"""
    You are the supervisor of a research assistant.

    Decide which agent should handle this query:

    - rag: use the internal knowledge base
    - research: use external web research

    User query:
    {query}

    Return only one word:
    rag
    or
    research
    """

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )

    return {
        "next_agent": content.strip().lower()
    }