from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import multiprocessing

class Request(BaseModel):
    query: str
    k: int

class Document(BaseModel):
    page_content: str
    metadata: Dict[str, str]

class Response(BaseModel):
    documents: List[Document]

def serve(model, host, port):
    app = FastAPI()

    @app.post("/retrieve", response_model=Response)
    async def retrieve(request: Request) -> Response:
        k = request.k if request.k > 0 else 1
        return [
            Document(
                page_content=doc["content"], metadata=doc.get("document_metadata", {})
            )
            for doc in model.search(query=request.query, k=k)
        ]

    uvicorn.run(app, host=host, port=port)