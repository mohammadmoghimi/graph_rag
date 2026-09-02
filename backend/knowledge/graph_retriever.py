from langchain_core.documents import Document
from .graph import Neo4jClient
from .entity_extractor import EntityExtractor
from .reranker import Reranker

class GraphRetriever:
    def __init__(self, retriever, website_ids, k=5):
        self.retriever = retriever
        self.website_ids = website_ids
        self.k = k
        self.reranker = Reranker()

    def retrieve(self, query):
        elastic_docs = self.retriever.invoke(query)
        # entities = EntityExtractor().extract(query)

        graph = Neo4jClient()

        try:
            # print("QUERY ENTITIES:", entities)

            graph_chunk_ids = graph.get_chunks_by_query(
                query,
                self.website_ids
            )

            print("GRAPH CHUNK IDS:", graph_chunk_ids)
            print("ELASTIC:", [
                d.metadata.get("chunk_id")
                for d in elastic_docs
            ])

        finally:
            graph.close()

        graph_docs = self._get_graph_documents(graph_chunk_ids)

        candidates = self._rrf(elastic_docs, graph_docs)

        print("GRAPH DOCS:", [
            d.metadata.get("chunk_id")
            for d in graph_docs
        ])

        print("RRF:", [
            d.metadata.get("chunk_id")
            for d in candidates
        ])

        final_docs = self.reranker.rerank(
            query,
            candidates,
            top_k=self.k
        )

        print("RERANKED:", [
            d.metadata.get("chunk_id")
            for d in final_docs
        ])

        return final_docs

    def _get_graph_documents(self, chunk_ids):
        if not chunk_ids:
            return []

        response = self.retriever.es_client.search(
            index=self.retriever.index_name,
            query={
                "terms": {
                    "metadata.chunk_id.keyword": chunk_ids
                }
            },
            size=len(chunk_ids),
            _source=["text", "metadata"]
        )

        return [
            Document(
                page_content=hit["_source"].get("text", ""),
                metadata=hit["_source"].get("metadata", {})
            )
            for hit in response["hits"]["hits"]
        ]

    def _rrf(self, elastic_docs, graph_docs, k=60):
        scores = {}
        documents = {}

        for rank, doc in enumerate(elastic_docs, start=1):
            doc_id = doc.metadata["chunk_id"]
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + k)
            documents[doc_id] = doc

        for rank, doc in enumerate(graph_docs, start=1):
            doc_id = doc.metadata["chunk_id"]
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + k)
            documents[doc_id] = doc

        ranked_ids = sorted(
            scores,
            key=scores.get,
            reverse=True
        )

        return [documents[doc_id] for doc_id in ranked_ids]