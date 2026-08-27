def supervisor(state):

    query = state['query']

    if 'latest' in query:
        next_agent = 'research'
    else:
        next_agent = 'rag'

    return {
        'next_agent': next_agent
    }