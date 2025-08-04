from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from src_agent.graphs.intent_graph import get_intent

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]
    intent_result: dict

def intent_node(state: AgentState):
    """Primeiro nó: chama o grafo de intenção."""
    print("--- Nó: Análise de Intenção ---")
    last_message = state['messages'][-1]
    user_input = last_message.content
    intent_data = get_intent(user_input)
    return {"intent_result": intent_data}


workflow = StateGraph(AgentState)
workflow.add_node("intent_node", intent_node)

workflow.set_entry_point("intent_node")

workflow.add_edge("intent_node", END)

workflow.compile()