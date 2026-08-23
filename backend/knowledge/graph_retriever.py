from langchain_core.documents import Document

from .graph import Neo4jClient


class GraphRetriever:
    def __init__(self, retriever):
        self.retriever = retriever

    def retrieve(self, query):
        documents = self.retriever.invoke(query)

        chunk_ids = [
            document.metadata["chunk_id"]
            for document in documents
            if "chunk_id" in document.metadata
        ]

        graph = Neo4jClient()

        try:
            graph_data = graph.get_chunk_graph(chunk_ids)
        finally:
            graph.close()

        return self._build_context(documents, graph_data)

    def _build_context(self, documents, graph_data):
        graph_by_chunk = {
            item["chunk_id"]: item
            for item in graph_data
        }

        results = []

        for document in documents:
            chunk_id = document.metadata.get("chunk_id")

            results.append(
                Document(
                    page_content=self._build_text(
                        document,
                        graph_by_chunk.get(chunk_id)
                    ),
                    metadata=document.metadata
                )
            )

        return results

    def _build_text(self, document, graph_data):
        if not graph_data:
            return document.page_content

        entities = graph_data["entities"]
        related = graph_data["related_entities"]
        communities = graph_data["communities"]

        context = document.page_content

        if entities:
            context += "\n\nEntities:\n"
            context += "\n".join(
                f"- {entity['name']} ({entity['type']})"
                for entity in entities
            )

        if related:
            context += "\n\nRelated entities:\n"
            context += "\n".join(
                f"- {entity['name']} ({entity['type']})"
                for entity in related
                if entity["name"]
            )

        if communities:
            context += "\n\nCommunity summaries:\n"
            context += "\n".join(
                f"- {community['summary']}"
                for community in communities
                if community["summary"]
            )

        return context