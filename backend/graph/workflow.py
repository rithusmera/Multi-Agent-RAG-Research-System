from langgraph.graph import StateGraph, START, END

from agents.supervisor import supervisor
from agents.research_agent import research_agent
from agents.rag_agent import rag_agent
from agents.evaluator import evaluator
from agents.response_agent import response_agent

from graph.state import ResearchState

def route_from_supervisor(state):
    if state['next_agent'] == 'rag':
        return 'rag'

    return 'research'

graph = StateGraph(ResearchState)

graph.add_node('supervisor', supervisor)
graph.add_node('research', research_agent)
graph.add_node('rag', rag_agent)
graph.add_node('evaluator', evaluator)
graph.add_node('response', response_agent)

graph.add_edge(START, 'supervisor')
graph.add_conditional_edges('supervisor', 
                            route_from_supervisor,
                            {
                                'rag': 'rag',
                                'research': 'research' 
                            })

graph.add_edge('research', 'evaluator')
graph.add_edge('rag', 'evaluator')
graph.add_edge('evaluator', 'response')
graph.add_edge('response', END)

app = graph.compile()