from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)

def langchain_code_splitter(
    documents: list[str], document_ids: list[str], chunk_size=256
):
    splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, chunk_size=chunk_size, chunk_overlap=0)
    chunks = []
    for doc_id, text in zip(document_ids, documents):
        chunks += [
            {"document_id": doc_id, "content": doc} for doc in splitter.split_text(text)
        ]

    return chunks