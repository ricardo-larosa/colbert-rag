import grpc
import argparse
from concurrent import futures
from colbertrag_pb2 import Response, Document
from colbertrag_pb2_grpc import add_ColbertRAGServicer_to_server, ColbertRAGServicer
from ragatouille import RAGPretrainedModel

RAGATOUILLE_PATH = "../.ragatouille/colbert/indexes"

class ColbertRAGServicer(ColbertRAGServicer):
    def __init__(self, model):
        self.RAG = model

    def Retrieve(self, request, context):
        """Get documents relevant to a query."""
        k = request.k if request.k > 0 else 1
        documents = [
            Document(
                page_content=doc["content"], metadata=doc.get("document_metadata", {})
            )
            for doc in self.RAG.search(query=request.query, k=k)
        ]
        
        return Response(documents=documents)

def serve(model, port, max_workers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    add_ColbertRAGServicer_to_server(ColbertRAGServicer(model), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()

def parse_arguments():
    parser = argparse.ArgumentParser(description="ColbertRAG server")
    parser.add_argument("--index_name", type=str, help="Path to the ColbertRAG index")
    parser.add_argument("--port", type=int, default=50051, help="Port to run the server on (default: 50051)")
    parser.add_argument("--max_workers", type=int, default=10, help="Maximum number of workers (default: 10)")

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    RAG = RAGPretrainedModel.from_index(f'{RAGATOUILLE_PATH}/{args.index_name}')
    serve(RAG, args.port, args.max_workers)