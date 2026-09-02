from sentence_transformers import CrossEncoder
import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"   # For transformers/sentence-transformers
os.environ["HF_HUB_OFFLINE"] = "1"  

class Reranker:
    def __init__(self):
        self.model = CrossEncoder("BAAI/bge-reranker-v2-m3")

    def rerank(self, query, documents, top_k=5):
        if not documents:
            return []

        pairs = [
            (query, document.page_content)
            for document in documents
        ]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [document for document, _ in ranked[:top_k]]