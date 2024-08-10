import argparse
from typing import Any, Callable, Optional, Union, List
from ragatouille import RAGPretrainedModel
from gitrepo import get_collections, RepoCloneError, FileProcessingError
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
import logging

# RAGATOUILLE_PATH = "../.ragatouille/colbert/indexes"
def parse_list(s):
    if s:
        return s.split(',')
    return []

def parse_arguments():
    parser = argparse.ArgumentParser(description="ColbertRAG indexer")
    parser.add_argument("--action", choices=['create', 'update'], default='create', help="Action (default: create)")
    parser.add_argument("--name", type=str, help="The name of the index")
    parser.add_argument("--repo_name", type=str, help="The name of the GitHub repository in the format username/repo-name")
    parser.add_argument("--chunk_size", type=int, default=256, help="Port to run the server on (default: 256)")
    parser.add_argument("--log_level", type=str, default="INFO", help="Log level (default: INFO)")
    parser.add_argument("--use_faiss", type=bool, default=False, help="Use Faiss for indexing (default: True)")
    parser.add_argument("--ext_blacklist", type=parse_list, default=".gitignore", help="Blacklisted file extensions (default: .gitignore)")
    parser.add_argument("--dir_blacklist", type=parse_list, default=".git,.github", help="Blacklisted directories (default: .git, .github)")

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

def index_git_repo(
        model_name:str, index_name:str, repo_name:str,
        ext_blacklist = {}, 
        dir_blacklist = {}, 
        max_document_length: int = 256, 
        split_documents: bool = True,
        use_faiss: bool = False) -> str:
    try:
        collections = get_collections(repo_name, ext_blacklist, dir_blacklist)
        logging.info(f"git repo {repo_name} cloned.")
    except RepoCloneError as e:
        logging.error(f"Repository cloning failed: {e}")
    except FileProcessingError as e:
        logging.error(f"File processing failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        logging.info("Respository {repo_name} cloned succesfully. ")

    # Determine the main language, collection with the most documents
    main_lang = max(collections, key=lambda x: len(collections[x][0]))
    collection, document_ids, document_metadatas = collections.get(main_lang, ([], [], []))

    logging.info(f"indexing {len(collection)} {main_lang} files ...")
    path = make_index(
        model_name=model_name,
        index_name=index_name,
        collection=collection,
        document_ids=document_ids,
        document_metadatas=document_metadatas,
        document_splitter_fn=lambda documents, document_ids, chunk_size=max_document_length: [{"document_id": doc_id, "content": chunk}
            for doc_id, text in zip(document_ids, documents)
            for chunk in RecursiveCharacterTextSplitter.from_language(
                language=Language[main_lang],
                chunk_size=chunk_size, 
                chunk_overlap=0
            ).split_text(text)
        ],
        max_document_length=max_document_length,
        split_documents=split_documents,
        use_faiss=use_faiss
    )

    for lang, (new_collection, new_document_ids, new_document_metadatas) in collections.items():
        if lang in [main_lang,'UNSUPPORTED','UNKNOWN']:
            continue
        logging.info(f"adding {len(new_collection)} {lang} files ...")
        update_index(
            model_path=path,
            index_name=index_name,
            new_collection=new_collection,
            new_document_ids=new_document_ids,
            new_document_metadatas=new_document_metadatas,
            document_splitter_fn=lambda documents, document_ids, chunk_size=max_document_length: [{"document_id": doc_id, "content": chunk}
                for doc_id, text in zip(document_ids, documents)
                for chunk in RecursiveCharacterTextSplitter.from_language(
                    language=Language[lang],
                    chunk_size=chunk_size, 
                    chunk_overlap=0
                ).split_text(text)
            ],
            split_documents=split_documents,
            use_faiss=use_faiss)

    return path

if __name__ == '__main__':
    args = parse_arguments()
    if args.log_level is not None:
        logging.basicConfig(level=args.log_level)
    # ext_blacklist = {'.exe', '.dll', '.so', '.dylib', '.png', '.jpg', '.jpeg', '.gif', '.rst', '.txt', '.yaml','.gitignore'}
    # dir_blacklist = {'ext','tests', 'docs', '.git', '.github'}

    if args.action == 'create':
        print(args.ext_blacklist)
        path = index_git_repo(
            model_name="colbert-ir/colbertv2.0",
            index_name=args.name,
            repo_name=args.repo_name,
            ext_blacklist=args.ext_blacklist,
            dir_blacklist=args.dir_blacklist,
            max_document_length=args.chunk_size,
            use_faiss=args.use_faiss)
        logging.info(f"created index in {path}")   
