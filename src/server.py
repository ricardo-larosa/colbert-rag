import grpc
import argparse
from concurrent import futures
from colbertrag_pb2 import Response, Document
from colbertrag_pb2_grpc import add_ColbertRAGServicer_to_server, ColbertRAGServicer
from ragatouille import RAGPretrainedModel
from wikipedia import get_wikipedia_page

RAGATOUILLE_PATH = "../.ragatouille/colbert/indexes"

class ColbertRAGServicer(ColbertRAGServicer):
    def __init__(self, model):
        self.RAG = model

    def Retrieve(self, request, context):
        k = request.k if request.k > 0 else 1
        retriever = self.RAG.as_langchain_retriever(k=k)
        documents = [Document(page_content=doc.page_content, metadata=doc.metadata)
                     for doc in retriever.invoke(request.query)]
        return Response(documents=documents)

def serve(model, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_ColbertRAGServicer_to_server(ColbertRAGServicer(model), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()

def parse_arguments():
    parser = argparse.ArgumentParser(description="ColbertRAG server")
    parser.add_argument("--index_name", type=str, help="Path to the ColbertRAG index")
    parser.add_argument("--port", type=int, default=50051, help="Port to run the server on (default: 50051)")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    RAG = RAGPretrainedModel.from_index(f'{RAGATOUILLE_PATH}/{args.index_name}')
    serve(RAG, args.port)