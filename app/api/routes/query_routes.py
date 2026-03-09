from fastapi import APIRouter
from core.retriever import SmartRetriever, MultiCollectionRetriever
from core.source_formatter import SourceFormatter
from core.storage_manager import StorageManager

router = APIRouter()
formatter = SourceFormatter()


@router.get("/collections")
def list_collections():
    sm = StorageManager()
    return sm.list_collections()


@router.post("/query")
def query_documents(query: str, collection: str | None = None):

    if collection:
        retriever = SmartRetriever(collection)
        response = retriever.query(query)
    else:
        retriever = MultiCollectionRetriever()
        response = retriever.query_best(query)

    sources = formatter.format_for_json(response.source_nodes)

    return {
        "answer": response.answer,
        "sources": sources
    }