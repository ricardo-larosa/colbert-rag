import logging
from typing import Any,Set
from ragatouille import RAGPretrainedModel
from colbert_rag.config import COLBERTRAG_CHUNK_SIZE
from colbert_rag.data.git_repo import get_collections
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

def index_git_repo(
        model_name: str,
        index_name: str,
        repo_name: str,
        ext_blacklist: Set[str] = set(),
        dir_blacklist: Set[str] = set(),
        max_document_length: int = COLBERTRAG_CHUNK_SIZE,
        split_documents: bool = True,
        use_faiss: bool = False,
        logging_level: str = "INFO"
) -> Any:
    logging.basicConfig(level=logging_level)
    try:
        collections = get_collections(repo_name, ext_blacklist, dir_blacklist)
        logging.info(f"Git repo {repo_name} cloned.")
    except Exception as e:
        logging.error(f"An error occurred while cloning the repository: {e}")
        return ""

    # Determine the main language, collection with the most documents
    main_lang = max(collections, key=lambda x: len(collections[x][0]))
    collection, document_ids, document_metadatas = collections.get(main_lang, ([], [], []))

    logging.info(f"Indexing {len(collection)} {main_lang} files ...")
    RAG = RAGPretrainedModel.from_pretrained(model_name)
    path = RAG.index(
        collection=collection,
        index_name=index_name,
        document_ids=document_ids,
        document_metadatas=document_metadatas,
        max_document_length=max_document_length,
        split_documents=split_documents,
        document_splitter_fn=lambda documents, document_ids, chunk_size=max_document_length: [{"document_id": doc_id, "content": chunk}
            for doc_id, text in zip(document_ids, documents)
            for chunk in RecursiveCharacterTextSplitter.from_language(
                language=Language[main_lang],
                chunk_size=chunk_size, 
                chunk_overlap=0
            ).split_text(text)
        ],
        use_faiss=use_faiss
    )

    for lang, (new_collection, new_document_ids, new_document_metadatas) in collections.items():
        if lang in [main_lang, 'UNSUPPORTED', 'UNKNOWN']:
            continue
        logging.info(f"Adding {len(new_collection)} {lang} files ...")
        RAG.add_to_index(
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
            use_faiss=use_faiss
        )

    return path
