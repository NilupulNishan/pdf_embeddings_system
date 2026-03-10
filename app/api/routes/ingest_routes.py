"""
PDF ingestion endpoint — upload a PDF file and process it into a collection.
"""
import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from core.pdf_loader import PDFLoader
from core.embeddings import EmbeddingsManager
from core.chunker import DocumentChunker
from core.storage_manager import StorageManager
from app.api.schemas import IngestResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and process it into a searchable collection.

    - Saves the uploaded file to a temporary location
    - Runs the full pipeline: load → chunk → embed → store
    - Returns the collection name, page count, and status
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Write upload to a named temp file so PDFLoader can open it by path
    try:
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    try:
        # Rename temp file to match original filename so collection name is derived correctly
        named_path = tmp_path.parent / file.filename
        tmp_path.rename(named_path)
        tmp_path = named_path

        # Initialize pipeline components
        pdf_loader = PDFLoader()
        embeddings_manager = EmbeddingsManager()
        chunker = DocumentChunker(embeddings_manager.get_llm())
        storage_manager = StorageManager()

        # Load PDF
        page_documents, collection_name = pdf_loader.load_pdf(tmp_path)

        # Chunk & enrich
        all_nodes, enriched_nodes = chunker.process_documents(page_documents)

        # Save to vector store
        success = storage_manager.save_collection(
            collection_name,
            all_nodes,
            enriched_nodes,
            embeddings_manager.get_embed_model(),
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to save collection to storage.")

        logger.info(f"Ingested '{file.filename}' → collection '{collection_name}' ({len(page_documents)} pages)")

        return IngestResponse(
            collection=collection_name,
            filename=file.filename,
            pages=len(page_documents),
            status="success",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion failed for '{file.filename}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Always clean up the temp file
        if tmp_path.exists():
            tmp_path.unlink()
