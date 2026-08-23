# from langchain_ollama import OllamaEmbeddings
# import os

# def get_embedding_model():
#     return OllamaEmbeddings(
#         model="embeddinggemma:300m"
#     )
import os
import requests
from typing import List
from django.conf import settings


class FastAPIEmbeddings:
    """
    A custom embedding class that calls your Colab FastAPI /embed endpoint.
    """
    
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or os.getenv("LLM_ENDPOINT_EMBED")
        if not self.endpoint:
            raise ValueError("LLM_ENDPOINT_EMBED environment variable is not set")
        
        # Ensure the endpoint ends with /embed
        if not self.endpoint.endswith("/embed"):
            self.endpoint = self.endpoint.rstrip("/") + "/embed"
        
        print(f"Using embedding endpoint: {self.endpoint}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents (used by LangChain for indexing).
        """
        embeddings = []
        total = len(texts)
        
        for idx, text in enumerate(texts):
            print(f"Embedding document {idx + 1}/{total}...")
            embedding = self.embed_query(text)
            embeddings.append(embedding)
        
        print(f"Finished embedding {total} documents.")
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text (used by LangChain for search).
        """
        try:
            response = requests.post(
                self.endpoint,
                json={"text": text},
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get embedding from FastAPI endpoint: {e}")
        
def get_embedding_model():
    return FastAPIEmbeddings()