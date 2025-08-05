import operator

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from src_agent.graphs.intent_graph import get_intent


class AgentState(TypedDict):
    input: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
    intent_result: dict


def intent_node(state: AgentState):
    """Recebe o state e chama o grafo de intenção para analisar o input."""
    user_input = state['input']
    intent_data = get_intent(user_input)
    return {"intent_result": intent_data}


def create_orchestrator_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("intent_node", intent_node)
    workflow.set_entry_point("intent_node")
    workflow.add_edge("intent_node", END)
    return workflow.compile()
