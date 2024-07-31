from ragatouille import RAGPretrainedModel
from wikipedia import get_wikipedia_page

def make_index(name, pages, max_document_length=180, split_documents=True):
    RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
    collection = [get_wikipedia_page(page) for page in pages]

    RAG.index(
        collection=collection,
        index_name=name,
        max_document_length=max_document_length,
        split_documents=split_documents,
    )

if __name__ == '__main__':
    name = "US_Elections-2024"
    pages = ["2024_United_States_presidential_election", "2024_United_States_elections"]
    make_index(name=name, pages=pages)