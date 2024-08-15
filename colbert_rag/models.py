from pydantic import BaseModel
from typing import List, Dict

class Request(BaseModel):
    query: str
    k: int

class Document(BaseModel):
    page_content: str
    metadata: Dict[str, str]

class Response(BaseModel):
    documents: List[Document]
