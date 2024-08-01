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

def serve(model, host, port) -> Response:    
    app = FastAPI()
    @app.post("/retrieve", response_model=Response)
    async def retrieve(request: Request) -> Response:
        k = request.k if request.k > 0 else 1
        documents = [
            Document(
                page_content=doc["content"], metadata=doc.get("document_metadata", {})
            )
            for doc in model.search(query=request.query, k=k)
        ]
        
        try:
            return Response(documents=documents)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    uvicorn.run(app, host=host, port=port)