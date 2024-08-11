import grpc

from concurrent import futures
from colbert_rag.server.base import BaseServer
from colbert_rag.models import Request, Response, Document
from colbert_rag.proto import colbertrag_pb2, colbertrag_pb2_grpc

class ColbertRAGServicer(colbertrag_pb2_grpc.ColbertRAGServicer):
    def __init__(self, server):
        self.server = server

    def Retrieve(self, 
                 request: colbertrag_pb2.Request, 
                 context: grpc.ServicerContext) -> colbertrag_pb2.Response:
        response = self.server.retrieve(Request(query=request.query, k=request.k))
        return colbertrag_pb2.Response(
            documents=[
                colbertrag_pb2.Document(
                    page_content=doc.page_content,
                    metadata=doc.metadata
                )
                for doc in response.documents
            ]
        )


class GRPCServer(BaseServer):
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

    def serve(self, host: str, port: int, max_workers: int = 10) -> None:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        colbertrag_pb2_grpc.add_ColbertRAGServicer_to_server(ColbertRAGServicer(self), server)
        server.add_insecure_port(f'{host}:{port}')
        server.start()
        server.wait_for_termination()
