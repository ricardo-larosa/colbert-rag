import argparse
from ragatouille import RAGPretrainedModel
from gitrepo import get_repo, RepoCloneError, FileProcessingError
import logging

# RAGATOUILLE_PATH = "../.ragatouille/colbert/indexes"

def parse_arguments():
    parser = argparse.ArgumentParser(description="ColbertRAG indexer")
    parser.add_argument("--action", choices=['create', 'update'], default='create', help="Action (default: create)")
    parser.add_argument("--name", type=str, help="The name of the index")
    parser.add_argument("--repo_name", type=str, help="The name of the GitHub repository in the format username/repo-name")
    parser.add_argument("--chunk_size", type=int, default=180, help="Port to run the server on (default: 512)")
    parser.add_argument("--log_level", type=str, default="INFO", help="Log level (default: INFO)")

    return parser.parse_args()

def make_index(model_name:str, index_name:str, repo_name:str, blacklist = {}, max_document_length=180, split_documents=True) -> str:
    logging.info(f"loading pretrained model {model_name}...")
    RAG = RAGPretrainedModel.from_pretrained(model_name)
    logging.info(f"pretrained model {model_name} loaded.")
    try:
        collection, metadata = get_repo(repo_name, blacklist)
        logging.info(f"git repo {repo_name} cloned.")
    except RepoCloneError as e:
        logging.error(f"Repository cloning failed: {e}")
    except FileProcessingError as e:
        logging.error(f"File processing failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        logging.info("Respository {repo_name} cloned succesfully. ")

    return RAG.index(
            collection=collection,
            index_name=index_name,
            max_document_length=max_document_length,
            split_documents=split_documents,
            document_metadatas=metadata,
        )


if __name__ == '__main__':
    args = parse_arguments()
    if args.log_level is not None:
        logging.basicConfig(level=args.log_level)
    blacklist = {'.exe', '.dll', '.so', '.dylib', '.png', '.jpg', '.jpeg', '.gif', '.rst', '.txt'}
    if args.action == 'create':
        path = make_index(
            model_name="colbert-ir/colbertv2.0",
            index_name=args.name,
            repo_name=args.repo_name,
            blacklist=blacklist,
            max_document_length=args.chunk_size
        )
        logging.info(f"created index in {path}")   
    elif args.action == 'update':
        print("Not implemented")
