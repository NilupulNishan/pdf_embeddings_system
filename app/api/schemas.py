from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    query: str
    session_id: str
    collection: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: Optional[dict]


class IngestResponse(BaseModel):
    collection: str
    filename: str
    pages: int
    status: str