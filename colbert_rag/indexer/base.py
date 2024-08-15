import logging
from typing import Any, Callable, Optional, Union, List
from ragatouille import RAGPretrainedModel

def make_index(
        model_name:str, index_name:str,  
        collection: list[str],
        document_ids: Any | List = None,
        document_metadatas: list[dict] | None = None,
        document_splitter_fn:Optional[Union[Callable, list[Callable]]] = None, 
        max_document_length: int = 256, 
        split_documents: bool = True, use_faiss: bool = True) -> Any:
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
        split_documents: bool = True, use_faiss: bool = False) -> None:
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
