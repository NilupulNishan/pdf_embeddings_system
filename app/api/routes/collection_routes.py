from fastapi import APIRouter
from core.storage_manager import StorageManager

router = APIRouter()


@router.get("/collections")
def list_collections():

    sm = StorageManager()
    collections = sm.list_collections()

    return {
        "collections": collections
    }