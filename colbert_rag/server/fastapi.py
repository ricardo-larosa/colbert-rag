from fastapi import FastAPI, HTTPException
import uvicorn
from colbert_rag.server.base import BaseServer
from colbert_rag.models import Request, Response, Document

class FastAPIServer(BaseServer):
    def retrieve(self, request: Request) -> Response:
        k = max(request.k, 1)
        documents = [
            Document(
                page_content=doc["content"],
                metadata=doc.get("document_metadata", {})
            )
            for doc in self.model.search(query=request.query, k=k)
        ]
        return Response(documents=documents)

    def serve(self, host: str, port: int) -> None:
        app = FastAPI()

        @app.post("/retrieve", response_model=Response)
        async def retrieve(request: Request) -> Response:
            try:
                return self.retrieve(request)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

        uvicorn.run(app, host=host, port=port)