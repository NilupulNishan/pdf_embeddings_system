import sys
import io

# Force UTF-8 encoding (fix Windows charmap errors)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from fastapi import FastAPI

from app.api.routes.query_routes import router as query_router
from app.api.routes.collection_routes import router as collection_router
from app.api.routes.health_routes import router as health_router
from app.api.routes.ingest_routes import router as ingest_router


app = FastAPI(
    title="PDF RAG API",
    description="Retrieval Augmented Generation system for querying PDFs",
    version="1.0"
)

app.include_router(query_router, prefix="/api", tags=["Query"])
app.include_router(collection_router, prefix="/api", tags=["Collections"])
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(ingest_router, prefix="/api", tags=["Ingest"])