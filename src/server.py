import grpc
from concurrent import futures
from colbertrag_pb2 import Response, Document
from colbertrag_pb2_grpc import add_ColbertRAGServicer_to_server, ColbertRAGServicer
from ragatouille import RAGPretrainedModel
from wikipedia import get_wikipedia_page

RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
pages = ["2024_United_States_presidential_election", "2024_United_States_elections"]
collection = [get_wikipedia_page(page) for page in pages]
RAG.index(
    collection=collection,
    index_name="US_Elections-2024",
    max_document_length=180,
    split_documents=True,
)

class ColbertRAGServicer(ColbertRAGServicer):
    def Retrieve(self, request, context):
        k = request.k if request.k > 0 else 1
        retriever = RAG.as_langchain_retriever(k=k)
        documents = [Document(page_content=doc.page_content, metadata=doc.metadata) 
                     for doc in retriever.invoke(request.query)]

        return Response(documents=documents)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_ColbertRAGServicer_to_server(ColbertRAGServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
