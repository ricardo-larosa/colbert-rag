import argparse
import logging
from colbert_rag.indexer.git_repo import index_git_repo

def parse_list(s):
    if s:
        return s.split(',')
    return []

def parse_arguments():
    parser = argparse.ArgumentParser(description="ColbertRAG indexer")
    parser.add_argument("--name", type=str, help="The name of the index")
    parser.add_argument("--repo_name", type=str, help="The name of the GitHub repository in the format username/repo-name")
    parser.add_argument("--chunk_size", type=int, default=256, help="Port to run the server on (default: 256)")
    parser.add_argument("--log_level", type=str, default="INFO", help="Log level (default: INFO)")
    parser.add_argument("--use_faiss", type=bool, default=False, help="Use Faiss for indexing (default: True)")
    parser.add_argument("--ext_blacklist", type=parse_list, default=".gitignore", help="Blacklisted file extensions (default: .gitignore)")
    parser.add_argument("--dir_blacklist", type=parse_list, default=".git,.github", help="Blacklisted directories (default: .git, .github)")

    return parser.parse_args()

def create() -> None:
    args = parse_arguments()
    path = index_git_repo(
        model_name="colbert-ir/colbertv2.0",
        index_name=args.name,
        repo_name=args.repo_name,
        ext_blacklist=args.ext_blacklist,
        dir_blacklist=args.dir_blacklist,
        max_document_length=args.chunk_size,
        use_faiss=args.use_faiss,
        logging_level=args.log_level)
    print(f'Index {args.name} created at {path}')
