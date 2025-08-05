import operator
from typing import TypedDict, Annotated, Sequence, Literal

from langchain_core.messages import BaseMessage, AIMessage
from langgraph.graph import StateGraph, END

from src_agent.graphs.intent_graph import intent_graph_runnable


class AgentState(TypedDict):
    input: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
    intent_result: dict


def intent_node(state: AgentState):
    """Chama o sub-grafo de intenção para analisar a mensagem do usuário."""    
    graph_input = {"user_message": state["input"]}
    intent_data = intent_graph_runnable.invoke(graph_input, state)
    
    return {"intent_result": intent_data.get('intent_result', {})}

def editor_node(state: AgentState):
    """Placeholder para o futuro Agente Editor."""
    print("--- Orquestrador: Roteado para o Agente Editor (Placeholder) ---")
    message = AIMessage(content="[Placeholder] Ok, entendi que preciso agendar ou atualizar uma tarefa.")
    return {"messages": [message]}

def analyst_node(state: AgentState):
    """Placeholder para o futuro Agente Analista."""
    print("--- Orquestrador: Roteado para o Agente Analista (Placeholder) ---")
    message = AIMessage(content="[Placeholder] Ok, entendi que preciso consultar seu calendário.")
    return {"messages": [message]}

def clarification_node(state: AgentState):
    """Nó que lida com a necessidade de clarificação."""
    print("--- Orquestrador: Roteado para Clarificação ---")
    question = state["intent_result"].get("clarification_question", "Não entendi bem, pode reformular?")
    message = AIMessage(content=question)
    return {"messages": [message]}

def general_response_node(state: AgentState):
    """Nó para conversas gerais ou falhas."""
    print("--- Orquestrador: Roteado para Conversa Geral ---")
    message = AIMessage(content="Olá! Sou seu assistente de calendário. Como posso ajudar?")
    return {"messages": [message]}


def route_after_intent(state: AgentState) -> Literal[
    "ask_clarification", "call_editor", "call_analyst", "general_conversation", "__end__"
]:
    """Inspeciona o resultado da intenção e decide para onde ir."""
    is_ambiguous = state["intent_result"].get("is_ambiguous", False)
    intent = state["intent_result"].get("intent")

    if is_ambiguous:
        return "ask_clarification"
    
    if intent == "AGENDAR_TAREFA" or intent == "ATUALIZAR_STATUS_TAREFA":
        return "call_editor"
    
    if intent == "CONSULTAR_CALENDARIO":
        return "call_analyst"
    
    return "general_conversation"


def create_orchestrator_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("intent_node", intent_node)
    workflow.add_node("editor_node", editor_node)
    workflow.add_node("analyst_node", analyst_node)
    workflow.add_node("clarification_node", clarification_node)
    workflow.add_node("general_response_node", general_response_node)

    workflow.set_entry_point("intent_node")

    workflow.add_conditional_edges(
        "intent_node",
        route_after_intent,
        {
            "ask_clarification": "clarification_node",
            "call_editor": "editor_node",
            "call_analyst": "analyst_node",
            "general_conversation": "general_response_node"
        }
    )
    workflow.add_edge("clarification_node", END)
    workflow.add_edge("editor_node", END)
    workflow.add_edge("analyst_node", END)
    workflow.add_edge("general_response_node", END)

    return workflow.compile()
