from django.utils import timezone

from knowledge.embeddings import get_embedding_model
from knowledge.indexer import index_chunks
from knowledge.entity_extractor import EntityExtractor
from knowledge.graph import Neo4jClient
from .pipeline import document_to_chunks


def process_document(document):
    document.status = "processing"
    document.save(update_fields=["status", "updated_at"])

    try:
        chunks = document_to_chunks(document)

        embeddings = get_embedding_model()
        index_chunks(chunks, embeddings)

        build_graph(document, chunks)

        document.status = "completed"
        document.save(update_fields=["status", "updated_at"])

        return chunks

    except Exception as error:
        document.status = "failed"
        document.save(update_fields=["status", "updated_at"])
        raise error


def build_graph(document, chunks):
    extractor = EntityExtractor()
    graph = Neo4jClient()

    try:
        for chunk in chunks:
            graph.create_document_chunk(document.id, chunk)

            entities = extractor.extract(chunk.page_content)

            for entity in entities:
                graph.create_entity(
                    chunk.metadata["chunk_id"],
                    entity
                )

            relationships = extractor.extract_relationships(
                chunk.page_content
            )

            for relationship in relationships:
                graph.create_relationship(relationship)
    finally:
        graph.close()