import logging
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents.supervisor import supervisor
from agents.research_agent import research_agent
from agents.rag_agent import rag_agent
from agents.evaluator import evaluator
from agents.human_node import human_node
from agents.response_agent import response_agent

from graph.state import ResearchState

logger = logging.getLogger(__name__)

def route_from_supervisor(state: ResearchState) -> str:
    """Conditional router for Supervisor Agent decisions."""
    next_agent = state.get("next_agent", "rag")
    if next_agent == "rag":
        return "rag"
    elif next_agent == "research":
        return "research"
    elif next_agent == "both":
        return "rag"
    elif next_agent == "human":
        return "human_node"
    elif next_agent == "response":
        return "response"
    return "rag"

def route_from_evaluator(state: ResearchState) -> str:
    """
    Conditional router for Evaluator Agent decisions.
    Determines whether information is sufficient to respond, needs another supervisor pass,
    or requires Human-in-the-loop (HITL) intervention.
    """
    evaluation = state.get("evaluation", {})
    iteration_count = state.get("iteration_count", 1)
    max_iterations = state.get("max_iterations", 2)

    is_sufficient = evaluation.get("is_sufficient", False)

    if is_sufficient:
        logger.info("[Evaluator Routing] Quality checks passed -> Routing to Response Agent.")
        return "response"
    
    if iteration_count < max_iterations:
        logger.info(f"[Evaluator Routing] Context insufficient (Iteration {iteration_count}/{max_iterations}) -> Routing back to Supervisor for retry loop.")
        return "supervisor"
    
    logger.info(f"[Evaluator Routing] Reached max iterations ({max_iterations}) -> Escalating to Human-in-the-loop (human_node).")
    return "human_node"

def route_from_human(state: ResearchState) -> str:
    """Conditional router following Human-in-the-loop review."""
    next_agent = state.get("next_agent", "response")
    if next_agent == "supervisor":
        return "supervisor"
    return "response"

# Build LangGraph workflow graph
graph_builder = StateGraph(ResearchState)

# Add Agent Nodes
graph_builder.add_node("supervisor", supervisor)
graph_builder.add_node("rag", rag_agent)
graph_builder.add_node("research", research_agent)
graph_builder.add_node("evaluator", evaluator)
graph_builder.add_node("human_node", human_node)
graph_builder.add_node("response", response_agent)

# Set Entry Edge
graph_builder.add_edge(START, "supervisor")

# Set Supervisor Conditional Edges
graph_builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "rag": "rag",
        "research": "research",
        "human_node": "human_node",
        "response": "response"
    }
)

# Set Agent Completion Edges
graph_builder.add_edge("rag", "evaluator")
graph_builder.add_edge("research", "evaluator")

# Set Evaluator Conditional Feedback Loop Edges
graph_builder.add_conditional_edges(
    "evaluator",
    route_from_evaluator,
    {
        "response": "response",
        "supervisor": "supervisor",
        "human_node": "human_node"
    }
)

# Set Human Node Edges
graph_builder.add_conditional_edges(
    "human_node",
    route_from_human,
    {
        "supervisor": "supervisor",
        "response": "response"
    }
)

# Set Response Completion Edge
graph_builder.add_edge("response", END)

# Configure MemorySaver checkpointer for thread persistence, state inspection & HITL interrupts
checkpointer = MemorySaver()
app = graph_builder.compile(checkpointer=checkpointer, interrupt_before=["human_node"])