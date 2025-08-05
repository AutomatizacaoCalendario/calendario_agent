import datetime
from typing import TypedDict, Optional, Literal
from pydantic import BaseModel, Field

from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, END

from src_agent import config
from src_agent.prompts.intent_prompts import REASONING_PROMPT, FORMATTING_PROMPT
from src_agent.utils.date_parser import parse_date_from_text


class IntentGraphState(TypedDict):
    user_message: str
    reasoning: Optional[str]
    intent_result: Optional[dict]
    clarification_needed: bool


class Intent(BaseModel):
    """A intenção do usuário extraída do texto."""
    intent: Literal[
        "AGENDAR_TAREFA", 
        "CONSULTAR_CALENDARIO", 
        "ATUALIZAR_STATUS_TAREFA", 
        "CONVERSA_GERAL"
    ] = Field(
        ...,
        description="A intenção principal do usuário."
    )
    task_description: Optional[str] = Field(
        None, 
        description="A descrição completa da tarefa ou pergunta. Ex: 'entregar o relatório de química'."
    )
    target_date: Optional[str] = Field(
        None, 
        description="A data alvo da tarefa no formato AAAA-MM-DD. Use a data de hoje se nenhuma for especificada."
    )
    timeframe_text: Optional[str] = Field(
        None,
        description="O texto original que o usuário usou para a data. Ex: 'amanhã', 'sexta-feira'."
    )
    is_ambiguous: bool = Field(
        False, 
        description="Defina como 'true' apenas se a intenção ou as entidades não estiverem 100% claras e uma pergunta de acompanhamento for necessária."
    )
    clarification_question: Optional[str] = Field(
        None,
        description="Se 'is_ambiguous' for 'true', formule uma pergunta clara para o usuário para resolver a ambiguidade."
    )


class IntentGraph:


    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=config.AZURE_OPENAI_DEPLOYMENT_NAME,
            openai_api_version=config.OPENAI_API_VERSION,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            temperature=0
        )
        self.graph = self._build_graph()


    def _build_graph(self):
        workflow = StateGraph(IntentGraphState)

        workflow.add_node("reasoning_node", self.reasoning_node)
        workflow.add_node("formatting_node", self.formatting_node)       
         
        workflow.set_entry_point("reasoning_node")

        workflow.add_edge("reasoning_node", "formatting_node")        
        workflow.add_conditional_edges(
            "formatting_node",
            self.should_clarify,
            {
                "clarify": END,
                "continue": END
            }
        )        
        return workflow.compile()


    def reasoning_node(self, state: IntentGraphState):
        today = datetime.date.today().strftime("%A, %Y-%m-%d")
        chain = REASONING_PROMPT | self.llm
        result = chain.invoke({"today": today, "user_message": state["user_message"]})
        return {"reasoning": result.content}


    def formatting_node(self, state: IntentGraphState):
        today = datetime.date.today()
        parser = PydanticOutputParser(pydantic_object=Intent)
        chain = FORMATTING_PROMPT | self.llm | parser

        response_intent = chain.invoke({
            "today": today.strftime("%A, %Y-%m-%d"),
            "reasoning": state["reasoning"],
            "user_message": state["user_message"],
            "format_instructions": parser.get_format_instructions()
        })
        
        intent_data = response_intent.dict()
        
        # Lógica do date_parser pra converter texto em data
        if intent_data.get("timeframe_text"):
            parsed_date = parse_date_from_text(intent_data["timeframe_text"])
            if parsed_date:
                intent_data["target_date"] = parsed_date
        
        elif intent_data.get("intent") == "AGENDAR_TAREFA" and not intent_data.get("target_date"):
            intent_data["target_date"] = today.strftime('%Y-%m-%d')
            
        return {"intent_result": intent_data, "clarification_needed": intent_data["is_ambiguous"]}


    def should_clarify(self, state: IntentGraphState) -> Literal["clarify", "continue"]:
        """O grafo precisa pedir clarificação ou pode continuar?"""
        if state["clarification_needed"]:
            return "clarify"
        else:
            return "continue"

intent_graph_runnable = IntentGraph().graph
