import requests
import ragatouille

# Wikipedia API endpoint
URL = "https://en.wikipedia.org/w/api.php"

def get_wikipedia_page(title: str):
    """
    Retrieve the full text content of a Wikipedia page.

    :param title: str - Title of the Wikipedia page.
    :return: str - Full text content of the page as raw string.
    """
    # Parameters for the API request
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "explaintext": True,
    }

    # Custom User-Agent header to comply with Wikipedia's best practices
    headers = {"User-Agent": "RAGatouille_tutorial/0.0.1 (ricardo@larosa.dev)"}

    response = requests.get(URL, params=params, headers=headers)
    data = response.json()

    # Extracting page content
    page = next(iter(data["query"]["pages"].values()))
    
    return page["extract"] if "extract" in page else None

def make_index(model, name, pages, max_document_length=180, split_documents=True):
    collection = [get_wikipedia_page(page) for page in pages]
    model.index(
        collection=collection,
        index_name=name,
        max_document_length=max_document_length,
        split_documents=split_documents,
    )
