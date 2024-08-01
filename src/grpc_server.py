import grpc

from concurrent import futures
from colbertrag_pb2 import Response, Document
from colbertrag_pb2_grpc import add_ColbertRAGServicer_to_server, ColbertRAGServicer

RAGATOUILLE_PATH = "../.ragatouille/colbert/indexes"

class ColbertRAGServicer(ColbertRAGServicer):
    def __init__(self, model):
        self.RAG = model

    def Retrieve(self, request, context)  -> Response:
        """Get documents relevant to a query."""
        k = request.k if request.k > 0 else 1
        documents = [
            Document(
                page_content=doc["content"], metadata=doc.get("document_metadata", {})
            )
            for doc in self.RAG.search(query=request.query, k=k)
        ]
        
        return Response(documents=documents)

def serve(model, host, port, max_workers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    add_ColbertRAGServicer_to_server(ColbertRAGServicer(model), server)
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    server.wait_for_termination()