# RAG with ColBERT 

Demos of RAG with ColBERT using [RAGatouille](https://github.com/bclavie/RAGatouille) and Langchain.

- ColBERT generates a contextually influenced vector for each token in the passages.
- Also, it generates vectors for each token in the query.
- Then, the score of each document is the sum of the maximum similarity of each query embedding to any of the document embeddings.

## Setup

### Generating protobuf file

```sh
python -m grpc_tools.protoc -I . --python_out=./src --pyi_out=./src --grpc_python_out=./src colbertrag.proto
```

## Examples

### Generating a Wikipedia Index

```python
from ragatouille import RAGPretrainedModel
from wikipedia import make_index

if __name__ == '__main__':
    RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
    name = "US_Elections-2024" # Index name
    pages = ["2024_United_States_presidential_election", "2024_United_States_elections"] # pages to Index
    make_index(model=RAG, name=name, pages=pages)
```

### Retrieving with a GRPC client

```python
import grpc
import colbertrag_pb2
import colbertrag_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = colbertrag_pb2_grpc.ColbertRAGStub(channel)
        response = stub.Retrieve(colbertrag_pb2.Request(query="Who are the presidential candidates for the elections in 2024", k=2))
        print("ColbertRAG client received:")
        for doc in response.documents:
            print(f"Page content: {doc.page_content}")
            print(f"Metadata: {doc.metadata}")
            print("---")

if __name__ == '__main__':
    run()
```

## Indexing a Git repo

```sh
python indexer.py --name pvlib --repo_name pvlib/pvlib-python --chunk_size=512
```
