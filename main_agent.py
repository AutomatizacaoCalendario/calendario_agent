import uvicorn
from fastapi import FastAPI
from src_agent.api import webhooks

app = FastAPI(
    title="Calendario Agent API",
    description="API para o agente de IA que gerencia o calendário via WhatsApp."
)

app.include_router(webhooks.router)

@app.get("/", tags=["Status"])
def read_root():
    """Endpoint root."""
    return {"status": "ok", "message": "Bem-vindo ao Calendario Agent!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)