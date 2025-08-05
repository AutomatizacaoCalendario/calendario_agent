import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src_agent import config

class Intent(BaseModel):
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


def get_intent(user_message: str) -> dict:
    """
    Analisa a mensagem do usuário usando prompt engineering e um parser de saída
    para garantir a compatibilidade com versões mais antigas da API do Azure.
    """
    llm = AzureChatOpenAI(
        azure_deployment=config.AZURE_OPENAI_DEPLOYMENT_NAME,
        openai_api_version=config.OPENAI_API_VERSION,
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_key=config.AZURE_OPENAI_API_KEY,
        temperature=0
    )

    # 1. Criamos uma instância do parser, usando nossa classe Pydantic como guia.
    parser = PydanticOutputParser(pydantic_object=Intent)

    # 2. Criamos um template de prompt que inclui as instruções de formatação do parser.
    #    Isso diz explicitamente ao LLM como formatar a saída.
    today = datetime.date.today().strftime("%A, %Y-%m-%d")
    prompt_template = ChatPromptTemplate.from_template(
        template="""Analise a mensagem do usuário. A data de hoje é {today}.
Sua tarefa é extrair a intenção e as entidades relevantes.
Responda APENAS com um objeto JSON, seguindo estritamente as instruções de formatação abaixo.
NÃO adicione nenhuma palavra ou comentário extra antes ou depois do JSON.

{format_instructions}

MENSAGEM DO USUÁRIO:
{user_message}
""",
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # 3. Criamos uma "cadeia" (chain) que conecta o prompt, o LLM e o parser.
    chain = prompt_template | llm | parser

    try:
        # 4. Invocamos a cadeia. Ela fará todo o trabalho: formata o prompt,
        #    chama o LLM, pega a resposta em texto e a converte para o nosso objeto Intent.
        response_intent = chain.invoke({"today": today, "user_message": user_message})
        return response_intent.dict()
        
    except Exception as e:
        print(f"Erro ao analisar a intenção: {e}")
        return {"intent": "FALHA_NA_ANALISE", "error": str(e)}
