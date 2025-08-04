from pymongo import MongoClient
from langchain_core.runnables.history import RunnableWithMessageHistory
from src_agent.graphs.orchestrator_graph import create_orchestrator_graph
from src_agent import config


def get_session_history(session_id: str):
    """
    Factory que cria uma instância de histórico de chat por thread_id
    usando o mongodb.
    """
    from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
    
    return MongoDBChatMessageHistory(
        connection_string=config.MONGO_URI,
        session_id=session_id,
        database_name="calendario_agent_db", # Nome do seu banco de dados
        collection_name="chat_histories"     # Nome da coleção onde as conversas serão salvas
    )

# --- Compilação do Agente com o Checkpointer ---

# 1. Cria o grafo base do orquestrador
orchestrator_graph = create_orchestrator_graph()

# 2. Envolve o grafo com a lógica de gerenciamento de histórico
#    Esta é a forma moderna e recomendada pelo LangChain de usar checkpoints.
agent_executor = RunnableWithMessageHistory(
    orchestrator_graph,
    get_session_history, # Passa a função factory que sabe como buscar/criar históricos
    input_messages_key="messages", # Diz ao LangGraph para procurar a entrada sob a chave "messages"
    history_messages_key="messages", # Diz para injetar o histórico de volta na chave "messages"
)