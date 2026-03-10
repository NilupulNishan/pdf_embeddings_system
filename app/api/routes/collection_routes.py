from fastapi import APIRouter, HTTPException
from core.storage_manager import StorageManager

router = APIRouter()


@router.get("/collections")
def list_collections():

    sm = StorageManager()
    collections = sm.list_collections()

    return {
        "collections": collections
    }


@router.get("/collections/{collection_name}")
def get_collection_info(collection_name: str):
    """Get details about a specific collection (chunk count, docstore status)."""

    sm = StorageManager()

    if not sm.collection_exists(collection_name):
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found.")

    info = sm.get_collection_info(collection_name)
    return info


@router.delete("/collections/{collection_name}")
def delete_collection(collection_name: str):
    """Delete a collection and its associated docstore."""

    sm = StorageManager()

    if not sm.collection_exists(collection_name):
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found.")

    success = sm.delete_collection(collection_name)

    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to delete collection '{collection_name}'.")

    return {"message": f"Collection '{collection_name}' deleted successfully."}