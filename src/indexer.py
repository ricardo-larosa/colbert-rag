import argparse
from typing import Any, Callable, Optional, Union, List
from ragatouille import RAGPretrainedModel
from gitrepo import get_repo, RepoCloneError, FileProcessingError
from preprocessors import langchain_code_splitter
import logging

# RAGATOUILLE_PATH = "../.ragatouille/colbert/indexes"

def parse_arguments():
    parser = argparse.ArgumentParser(description="ColbertRAG indexer")
    parser.add_argument("--action", choices=['create', 'update'], default='create', help="Action (default: create)")
    parser.add_argument("--name", type=str, help="The name of the index")
    parser.add_argument("--repo_name", type=str, help="The name of the GitHub repository in the format username/repo-name")
    parser.add_argument("--chunk_size", type=int, default=256, help="Port to run the server on (default: 256)")
    parser.add_argument("--log_level", type=str, default="INFO", help="Log level (default: INFO)")
    parser.add_argument("--use_faiss", type=bool, default=False, help="Use Faiss for indexing (default: True)")

    return parser.parse_args()

def make_index(
        model_name:str, index_name:str,  
        collection: list[str],
        document_ids: Any | List = None,
        document_metadatas: list[dict] | None = None,
        document_splitter_fn:Optional[Union[Callable, list[Callable]]] = None, 
        max_document_length: int = 256, 
        split_documents: bool = True, use_faiss: bool = True) -> str:
    logging.info(f"loading a pre-trained checkpoint {model_name}...")
    RAG = RAGPretrainedModel.from_pretrained(model_name)
    logging.info(f"pretrained model {model_name} loaded.")

    return RAG.index(
            collection=collection,
            index_name=index_name,
            max_document_length=max_document_length,
            split_documents=split_documents,
            document_metadatas=document_metadatas,
            document_ids=document_ids,
            document_splitter_fn=document_splitter_fn,
            use_faiss=use_faiss,
            overwrite_index=True
        )

def update_index(
        model_path:str, 
        index_name:str,
        new_collection: list[str],
        new_document_ids: Any | List = None,
        new_document_metadatas: list[dict] | None = None,
        document_splitter_fn:Optional[Union[Callable, list[Callable]]] = None,
        split_documents: bool = True, use_faiss: bool = False) -> str:
    logging.info(f"loading checkpoint from an existing index {model_path}...")
    RAG = RAGPretrainedModel.from_index(model_path)
    logging.info(f"existing checkpoint {model_path} loaded.")
    RAG.add_to_index(
        index_name=index_name,
        new_collection=new_collection,
        new_document_ids=new_document_ids,
        new_document_metadatas=new_document_metadatas,
        document_splitter_fn=document_splitter_fn,
        split_documents=split_documents,
        use_faiss=use_faiss)

def make_git_index(
        model_name:str, index_name:str, repo_name:str,
        ext_blacklist = {}, 
        dir_blacklist = {}, 
        max_document_length: int = 256, 
        split_documents: bool = True,
        use_faiss: bool = False) -> str:

    path = index_git_code(
        model_name=model_name,
        index_name=index_name,
        repo_name=repo_name,
        ext_blacklist=ext_blacklist,
        dir_blacklist=dir_blacklist,
        max_document_length=max_document_length,
        use_faiss=use_faiss)
    
    logging.info(f"indexing other files...")

    for filetype, (contents, ids, metadata) in collections.items():
        if filetype == "x-python" or filetype =="unknown":
            continue
        logging.info(f"indexing {filetype} files...")
        update_index(
            model_path=path,
            index_name=index_name,
            new_collection=contents,
            new_document_ids=ids,
            new_document_metadatas=metadata,
            split_documents=split_documents,
            use_faiss=use_faiss)

    return path

def index_git_code(
        model_name:str, index_name:str, repo_name:str,
        ext_blacklist = {}, 
        dir_blacklist = {}, 
        max_document_length: int = 256, 
        split_documents: bool = True,
        use_faiss: bool = False) -> str:
    try:
        collections = get_repo(repo_name, ext_blacklist, dir_blacklist)
        logging.info(f"git repo {repo_name} cloned.")
    except RepoCloneError as e:
        logging.error(f"Repository cloning failed: {e}")
    except FileProcessingError as e:
        logging.error(f"File processing failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        logging.info("Respository {repo_name} cloned succesfully. ")

    logging.info(f"indexing code ...")

    python_files = collections.get("x-python", ([], [], []))
    python_contents, python_ids, python_metadata = python_files
    path = make_index(
        model_name=model_name,
        index_name=index_name,
        collection=python_contents,
        document_ids=python_ids,
        document_metadatas=python_metadata,
        document_splitter_fn=langchain_code_splitter,
        max_document_length=max_document_length,
        split_documents=split_documents,
        use_faiss=use_faiss)

    return path

if __name__ == '__main__':
    args = parse_arguments()
    if args.log_level is not None:
        logging.basicConfig(level=args.log_level)
    ext_blacklist = {'.exe', '.dll', '.so', '.dylib', '.png', '.jpg', '.jpeg', '.gif', '.rst', '.txt', '.yaml','.gitignore'}
    dir_blacklist = {'ext','tests', 'docs', '.git', '.github'}
    # dir_blacklist = {'script','tests', 'doc', '.git', '.github'}
    if args.action == 'create':
        path = make_git_index(
            model_name="colbert-ir/colbertv2.0",
            index_name=args.name,
            repo_name=args.repo_name,
            ext_blacklist=ext_blacklist,
            dir_blacklist=dir_blacklist,
            max_document_length=args.chunk_size,
            use_faiss=args.use_faiss)
        logging.info(f"created index in {path}")   
    elif args.action == 'update':
        print("Not implemented")
