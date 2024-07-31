import grpc
import colbertrag_pb2
import colbertrag_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = colbertrag_pb2_grpc.ColbertRAGStub(channel)
        response = stub.Retrieve(colbertrag_pb2.Request(query="Hello, world!"))
        print("ColbertRAG client received:")
        for doc in response.documents:
            print(f"Page content: {doc.page_content}")
            print(f"Metadata: {doc.metadata}")
            print("---")

if __name__ == '__main__':
    run()