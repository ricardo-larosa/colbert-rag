import argparse
from ragatouille import RAGPretrainedModel
from colbert_rag.server.grpc import GRPCServer
from colbert_rag.server.fastapi import FastAPIServer
from colbert_rag.config import (
    RAGATOUILLE_PATH, COLBERTRAG_GRPC_PORT, COLBERTRAG_FASTAPI_PORT,
    COLBERTRAG_HOST, COLBERTRAG_MAX_WORKERS
)
import logging

def parse_arguments():
    parser = argparse.ArgumentParser(description="ColbertRAG server")
    parser.add_argument("--type", choices=['grpc', 'fastapi'], default='grpc', help="Server type (default: grpc)")
    parser.add_argument("--host", type=str, default=COLBERTRAG_HOST, help="Host to bind the server to")
    parser.add_argument("--index", type=str, required=True, help="Path to the ColbertRAG index")
    parser.add_argument("--port", type=int, help="Port to run the server on")
    parser.add_argument("--max_workers", type=int, default=COLBERTRAG_MAX_WORKERS, help="Maximum number of workers")
    parser.add_argument("--log_level", type=str, default="INFO", help="Log level (default: INFO)")

    return parser.parse_args()

def run():
    args = parse_arguments()
    logging.basicConfig(level=args.log_level)

    if args.port is None:
        args.port = COLBERTRAG_GRPC_PORT if args.type == 'grpc' else COLBERTRAG_FASTAPI_PORT

    RAG = RAGPretrainedModel.from_index(f'{RAGATOUILLE_PATH}/{args.index}')
    logging.info(f"Loaded index from {RAGATOUILLE_PATH}/{args.index}")

    if args.type == 'grpc':
        server = GRPCServer(RAG)
        server.serve(args.host, args.port, args.max_workers)
    elif args.type == 'fastapi':
        server = FastAPIServer(RAG)
        server.serve(args.host, args.port)