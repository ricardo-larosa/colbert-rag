# RAG with ColBERT 

Demos of RAG with ColBERT using [RAGatouille](https://github.com/bclavie/RAGatouille) and Langchain.

- ColBERT generates a contextually influenced vector for each token in the passages.
- Also, it generates vectors for each token in the query.
- Then, the score of each document is the sum of the maximum similarity of each query embedding to any of the document embeddings.

## Setup

### Generating protobuf file

```
python -m grpc_tools.protoc -I . --python_out=./src --pyi_out=./src --grpc_python_out=./src colbertrag.proto
```