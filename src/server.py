import grpc
from concurrent import futures
import colbertrag_pb2
import colbertrag_pb2_grpc
from ragatouille import RAGPretrainedModel

RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

class ColbertRAGServicer(colbertrag_pb2_grpc.ColbertRAGServicer):
    def Retrieve(self, request, context):
        k = request.k if request.k > 0 else 1
        retriever = RAG.as_langchain_retriever(k=k)
        documents = retriever.invoke(request.query)
        # Implement your query processing logic here
        # For example, let's create two dummy documents
        # doc1 = colbertrag_pb2.Document(
        #     page_content="Hello, world!",
        #     metadata={"source": "https://example.com"}
        # )
        # doc2 = colbertrag_pb2.Document(
        #     page_content="This is a sample document.",
        #     metadata={"source": "https://sample.com"}
        # )

        return colbertrag_pb2.Response(documents=documents)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    colbertrag_pb2_grpc.add_ColbertRAGServicer_to_server(ColbertRAGServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()