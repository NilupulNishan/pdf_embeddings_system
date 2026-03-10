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