from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from src_agent.graphs.orchestrator_graph import create_orchestrator_graph
from src_agent import config


def get_session_history(session_id: str):
    """
    Factory que cria uma instância de histórico de chat por thread_id
    usando o mongodb.
    """      
    return MongoDBChatMessageHistory(
        connection_string=config.MONGO_URI,
        session_id=session_id,
        database_name="calendario_agent_db",
        collection_name="chat_histories"
    )


orchestrator_graph = create_orchestrator_graph()

agent_executor = RunnableWithMessageHistory(
    orchestrator_graph,
    get_session_history,
    input_messages_key="input",
    history_messages_key="messages",
)
