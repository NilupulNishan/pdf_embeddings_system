from fastapi import APIRouter
from core.retriever import SmartRetriever, MultiCollectionRetriever
from core.source_formatter import SourceFormatter
from core.chat_memory import ChatMemoryManager
from app.api.schemas import QueryRequest

router = APIRouter()

formatter = SourceFormatter()

# store memory per session
chat_sessions = {}


@router.post("/query")
def query_documents(request: QueryRequest):

    session_id = request.session_id

    # create memory for new session
    if session_id not in chat_sessions:
        chat_sessions[session_id] = ChatMemoryManager()

    memory = chat_sessions[session_id]

    history = memory.get_context()

    context = ""
    if history:
        context = "\n".join(
            f"{msg.role.capitalize()}: {msg.content}"
            for msg in history
        )

    if context:
        query_with_memory = f"""
        Conversation history:
        {context}

        User question:
        {request.query}
        """
    else:
        query_with_memory = request.query

    # choose retriever
    if request.collection:
        retriever = SmartRetriever(request.collection)
        response = retriever.query(query_with_memory)
    else:
        retriever = MultiCollectionRetriever()
        response = retriever.query_best(query_with_memory)

    # save conversation
    memory.add_user_message(request.query)
    memory.add_assistant_message(response.answer)

    sources = formatter.format_for_json(response.source_nodes)

    return {
        "answer": response.answer,
        "sources": sources
    }


@router.delete("/memory/{session_id}")
def clear_memory(session_id: str):

    if session_id in chat_sessions:
        del chat_sessions[session_id]

    return {"message": "Memory cleared"}