import argparse
from ragatouille import RAGPretrainedModel
from gitrepo import get_repo, RepoCloneError, FileProcessingError
import logging

RAGATOUILLE_PATH = "../.ragatouille/colbert/indexes"

def parse_arguments():
    parser = argparse.ArgumentParser(description="ColbertRAG indexer")
    parser.add_argument("--action", choices=['create', 'update'], default='create', help="Action (default: create)")
    parser.add_argument("--name", type=str, help="The name of the index")
    parser.add_argument("--repo_name", type=str, help="The name of the GitHub repository in the format username/repo-name")
    parser.add_argument("--chunk_size", type=int, default=512, help="Port to run the server on (default: 512)")


    return parser.parse_args()

def make_index(index_name:str, repo_name:str, blacklist = {}, max_document_length=180, split_documents=True) -> str:
    logging.info("loading pretrained model ...")
    print("Hey hey")
    RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
    logging.info("pretrained model loaded.")
    try:
        collection, metadata = get_repo(repo_name, blacklist)
        logging.info("Respository {repo_name} cloned succesfully. ")
        return RAG.index(
            collection=collection,
            index_name=index_name,
            max_document_length=max_document_length,
            split_documents=split_documents,
            document_metadatas=metadata,
        )
    except RepoCloneError as e:
        logging.error(f"Repository cloning failed: {e}")
    except FileProcessingError as e:
        logging.error(f"File processing failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

# def update_index():
#     try:
#         collection, metadata = get_repo("pvlib/pvlib-python", blacklist)
#     except RepoCloneError as e:
#         print(f"Repository cloning failed: {e}")
#     except FileProcessingError as e:
#         print(f"File processing failed: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")

#     RAG = RAGPretrainedModel.from_index()
#     RAG.index(
#         collection=collection,
#         index_name=name,
#         max_document_length=max_document_length,
#         split_documents=split_documents,
#         document_metadatas=metadata,
#     )


if __name__ == '__main__':
    args = parse_arguments()
    blacklist = {'.exe', '.dll', '.so', '.dylib', '.png', '.jpg', '.jpeg', '.gif', '.rst', '.txt'}
    if args.action == 'create':
        path = make_index(args.name, args.repo_name, blacklist, 256)
        logging.info(f"created index in {path}")   
    elif args.action == 'update':
        print("Not implemented")
