# Em: src_agent/graphs/intent_graph.py

import datetime
from typing import Literal, Optional

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import AzureChatOpenAI

from src_agent import config

# --- Definição da Estrutura de Saída (O "Contrato") ---
# Usamos uma classe Pydantic para dizer ao LLM exatamente como queremos a resposta.

class Intent(BaseModel):
    """A intenção do usuário extraída do texto."""
    intent: Literal[
        "AGENDAR_TAREFA", 
        "CONSULTAR_CALENDARIO", 
        "ATUALIZAR_STATUS_TAREFA", 
        "CONVERSA_GERAL"
    ] = Field(
        ..., # ... significa que o campo é obrigatório
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


# --- Função Principal do Grafo ---

def get_intent(user_message: str) -> dict:
    """
    Analisa a mensagem do usuário e retorna um dicionário estruturado com a intenção.
    """
    # Nota: No LangGraph, isso se tornará um nó. Por enquanto, é uma função simples.
    
    llm = AzureChatOpenAI(
        azure_deployment=config.AZURE_OPENAI_DEPLOYMENT_NAME,
        openai_api_version=config.OPENAI_API_VERSION,
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_key=config.AZURE_OPENAI_API_KEY,
        temperature=0
    )

    # Usamos .with_structured_output para forçar o LLM a responder no formato da nossa classe Intent
    structured_llm = llm.with_structured_output(Intent)

    # A data de hoje é passada como contexto para o LLM saber o que é "hoje", "amanhã", etc.
    today = datetime.date.today().strftime("%A, %Y-%m-%d") # ex: Monday, 2025-08-04
    
    prompt = f"""
    Analise a seguinte mensagem do usuário. A data de hoje é {today}.
    Extraia a intenção e as entidades relevantes conforme a estrutura definida.

    Exemplos:
    - "marcar a entrega do projeto para sexta que vem" -> intent: AGENDAR_TAREFA
    - "o que eu tenho pra fazer amanhã?" -> intent: CONSULTAR_CALENDARIO
    - "a tarefa 'ligar para o orientador' já foi feita" -> intent: ATUALIZAR_STATUS_TAREFA
    - "oi tudo bem?" -> intent: CONVERSA_GERAL

    Mensagem do usuário: "{user_message}"
    """
    
    try:
        response_intent = structured_llm.invoke(prompt)
        # Convertemos o objeto Pydantic para um dicionário para fácil manipulação posterior
        return response_intent.dict()
    except Exception as e:
        print(f"Erro ao analisar a intenção: {e}")
        # Em caso de erro, podemos ter uma intenção padrão ou de falha
        return {"intent": "FALHA_NA_ANALISE", "error": str(e)}