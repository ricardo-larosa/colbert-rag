import argparse
from ragatouille import RAGPretrainedModel
import grpc_server
import fastapi_server
import logging

RAGATOUILLE_PATH = "../.ragatouille/colbert/indexes"

def parse_arguments():
    parser = argparse.ArgumentParser(description="ColbertRAG server")
    parser.add_argument("--server", choices=['grpc', 'fastapi'], default='grpc', help="Server type (default: grpc)")
    parser.add_argument("--host", type=str, help="Host to bind the server to")
    parser.add_argument("--index", type=str, help="Path to the ColbertRAG index")
    parser.add_argument("--port", type=int, help="Port to run the server on (default: 50051 or 8000)")
    parser.add_argument("--max_workers", type=int, default=10, help="Maximum number of workers (default: 10)")
    parser.add_argument("--log_level", type=str, default="INFO", help="Log level (default: INFO)")

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    if args.log_level is not None:
        logging.basicConfig(level=args.log_level)
    if args.port is None:
        args.port = 50051 if args.server == 'grpc' else 8000
    if args.host is None:
        args.host = '[::]' if args.server == 'grpc' else '0.0.0.0'

    RAG = RAGPretrainedModel.from_index(f'{RAGATOUILLE_PATH}/{args.index}')
    logging.info(f"Loaded index from {RAGATOUILLE_PATH}/{args.index}")
    if args.server == 'grpc':
        grpc_server.serve(RAG, args.host, args.port, args.max_workers)
    elif args.server == 'fastapi':
        fastapi_server.serve(RAG, args.host, args.port)