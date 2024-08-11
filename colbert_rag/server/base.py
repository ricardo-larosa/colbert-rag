from typing import Protocol, runtime_checkable
from colbert_rag.models import Request, Response
from ragatouille import RAGPretrainedModel

@runtime_checkable
class ServerProtocol(Protocol):
    def retrieve(self, request: Request) -> Response:
        ...

    def serve(self, host: str, port: int) -> None:
        ...

class BaseServer:
    def __init__(self, model: RAGPretrainedModel):
        self.model = model