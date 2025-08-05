import json

from fastapi import APIRouter, Form, Response
from twilio.rest import Client

from src_agent import config
from src_agent.core.agent_executor import agent_executor

twilio_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
router = APIRouter()


@router.post("/whatsapp")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    """
    Webhook que recebe a mensagem do WhatsApp e passa para o orquestrador.
    Return: resultado análise de intenção.
    """
    print(f"Mensagem recebida de {From}: {Body}")

    session_id = From
    graph_input = {"input": Body}
    graph_config = {"configurable": {"session_id": session_id}}

    final_state = agent_executor.invoke(graph_input, graph_config)

    last_message = final_state.get('messages', [])[-1]
    response_body = last_message.content if last_message else "Erro ao processar solicitação."

    print(f"Resposta final do Agente: {response_body}")
    
    try:
        twilio_client.messages.create(
            from_=config.TWILIO_PHONE_NUMBER,
            body=response_body,
            to=From
        )
    except Exception as e:
        print(f"[ERROR] erro ao enviar mensagem pelo twilio: {e}")

    return Response(status_code=204)
