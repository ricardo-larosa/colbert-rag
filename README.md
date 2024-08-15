# ColBERT RAG
Index GitHub repositories to ColBERT models and serve them with GRPC or FastAPI.

## Features

- ColBERT-based retrieval for contextually influenced token-level embeddings
- Support for indexing Git repositories with language specific chunking 
- GRPC and FastAPI server implementations
- Flexible document processing and indexing

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

The Apache License 2.0 is a permissive license that also provides an express grant of patent rights from contributors to users. Key points:

- It allows you to freely use, modify, distribute, and sell your software.
- If you modify the code, you may distribute your modified version, but you must include a notice stating that you changed the files.
- Any modifications or larger works may be distributed under different terms and without source code, but they must include a copy of the Apache 2.0 license.
- You must retain all copyright, patent, trademark, and attribution notices from the original code.

## Setup

1. Install dependencies using Poetry:

```sh
poetry install
```

2. Generate protobuf files:

```sh
poetry run generate-protos
```

## Usage

### Using Scripts

The project includes several utility scripts in the `/scripts` directory:

1. Generate Protobuf Files:
   ```sh
   poetry run generate-protos
   ```
   This script generates the necessary Python files from the protobuf definition.

2. Create Index:
   ```sh
   poetry run create-index --name <index_name>  --repo_name username/repo-name --chunk_size 512
   ```
   This script creates an index from a specified Git repository.

3. Run Server:
   ```sh
   poetry run server --type grpc|fastapi --index <index_name> 
   ```

4. Run Type Checking:
   ```sh
   poetry run type-check
   ```
   This script runs MyPy for type checking across the project.

### Indexing a Git Repository

```python
from colbert_rag.indexer.git_repo import index_git_repo

index_path = index_git_repo(
    model_name="colbert-ir/colbertv2.0",
    index_name="my-repo-index",
    repo_name="username/repo-name",
    max_document_length=512)
```

### Running the Server

#### GRPC Server

```python
from ragatouille import RAGPretrainedModel
from colbert_rag import GRPCServer
from colbert_rag.config import COLBERTRAG_GRPC_PORT, COLBERTRAG_HOST

model = RAGPretrainedModel.from_index("path/to/your/index")
server = GRPCServer(model)
server.serve(COLBERTRAG_HOST, COLBERTRAG_GRPC_PORT)
```

#### FastAPI Server

```python
from ragatouille import RAGPretrainedModel
from colbert_rag import FastAPIServer
from colbert_rag.config import COLBERTRAG_FASTAPI_PORT, COLBERTRAG_HOST

model = RAGPretrainedModel.from_index("path/to/your/index")
server = FastAPIServer(model)
server.serve(COLBERTRAG_HOST, COLBERTRAG_FASTAPI_PORT)
```

### Client Examples

#### GRPC Client

```python
import grpc
from colbert_rag.proto import colbertrag_pb2, colbertrag_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = colbertrag_pb2_grpc.ColbertRAGStub(channel)
        response = stub.Retrieve(colbertrag_pb2.Request(query="Your query here", k=2))
        print("ColbertRAG client received:")
        for doc in response.documents:
            print(f"Page content: {doc.page_content}")
            print(f"Metadata: {doc.metadata}")
            print("---")

if __name__ == '__main__':
    run()
```

#### FastAPI Client

Using Python with the `requests` library:

```python
import requests
import json

url = "http://localhost:8000/retrieve"
payload = {
    "query": "Your query here",
    "k": 2
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)

if response.status_code == 200:
    data = response.json()
    print("ColbertRAG client received:")
    for doc in data["documents"]:
        print(f"Page content: {doc['page_content']}")
        print(f"Metadata: {doc['metadata']}")
        print("---")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

Using curl:

```sh
curl -X POST "http://localhost:8000/retrieve" \
     -H "Content-Type: application/json" \
     -d '{"query": "Your query here", "k": 2}'
```

## Development

### Type Checking

Run MyPy for type checking:

```sh
poetry run type-check
```

### Running Tests

```sh
poetry run pytest
```
