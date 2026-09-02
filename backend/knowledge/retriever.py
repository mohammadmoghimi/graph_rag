from typing import List
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from elasticsearch import Elasticsearch
from typing import Any

class ElasticsearchHybridRetriever(BaseRetriever):

    es_client: Elasticsearch
    index_name: str
    embedding_model: Any
    website_ids: list[int] = []
    text_field: str = "text"
    embedding_field: str = "vector"
    k: int = 4
    num_candidates: int = 50
    bm25_weight: float = 0.5  
    vector_weight: float = 0.5  

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        query_vector = self.embedding_model.embed_query(query)

        bm25_body = {
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": [self.text_field]
                        }
                    },
                    "filter": {
                        "terms": {
                            "metadata.website_id": self.website_ids
                        }
                    }
                }
            },
            "size": self.num_candidates,
            "_source": [self.text_field, "metadata"]
        }
        bm25_response = self.es_client.search(index=self.index_name, body=bm25_body)
        bm25_hits = bm25_response["hits"]["hits"]

        knn_body = {
            "knn": {
                "field": self.embedding_field,
                "query_vector": query_vector,
                "k": self.num_candidates,
                "num_candidates": self.num_candidates,
                "filter": [
                    {
                        "terms": {
                            "metadata.website_id": self.website_ids
                        }
                    }
                ]
            },
            "size": self.num_candidates,
            "_source": [self.text_field, "metadata"]
        }
        knn_response = self.es_client.search(index=self.index_name, body=knn_body)
        knn_hits = knn_response["hits"]["hits"]

        combined_scores = {}
        doc_store = {} 

        for rank, hit in enumerate(bm25_hits, 1):
            doc_id = hit["_id"]
            score = hit["_score"]
            combined_scores[doc_id] = combined_scores.get(doc_id, 0) + (
                self.bm25_weight / (60 + rank)
            )
            doc_store[doc_id] = {
                "text": hit["_source"].get(self.text_field, ""),
                "metadata": hit["_source"].get("metadata", {})
            }

        for rank, hit in enumerate(knn_hits, 1):
            doc_id = hit["_id"]
            combined_scores[doc_id] = combined_scores.get(doc_id, 0) + (
                self.bm25_weight / (60 + rank)
            )
            if doc_id not in doc_store:
                doc_store[doc_id] = {
                    "text": hit["_source"].get(self.text_field, ""),
                    "metadata": hit["_source"].get("metadata", {})
                }

        sorted_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:self.k]

        documents = []
        for doc_id, score in sorted_docs:
            doc_data = doc_store[doc_id]
            documents.append(
                Document(
                    page_content=doc_data["text"],
                    metadata=doc_data["metadata"]
                )
            )
        return documents
    
    