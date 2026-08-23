from neo4j import GraphDatabase
from django.conf import settings


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(
                settings.NEO4J_USERNAME,
                settings.NEO4J_PASSWORD
            )
        )

    def close(self):
        self.driver.close()

    def create_chunk(self, website_id, chunk):
        with self.driver.session() as session:
            session.execute_write(
                self._create_chunk,
                website_id,
                chunk
            )

    def create_entity(self, chunk_id, entity):
        with self.driver.session() as session:
            session.execute_write(
                self._create_entity,
                chunk_id,
                entity
            )

    def create_relationship(self, relationship):
        with self.driver.session() as session:
            session.execute_write(
                self._create_relationship,
                relationship
            )


    @staticmethod
    def _create_chunk(tx, website_id, chunk):
        tx.run(
            """
            MERGE (website:Website {id: $website_id})
            MERGE (chunk:Chunk {id: $chunk_id})

            SET chunk.crawl_id = $crawl_id,
                chunk.source_url = $source_url

            MERGE (website)-[:HAS_CHUNK]->(chunk)
            """,
            website_id=website_id,
            chunk_id=chunk.metadata["chunk_id"],
            crawl_id=chunk.metadata["crawl_id"],
            source_url=chunk.metadata["source_url"]
        )
    @staticmethod
    def _create_entity(tx, chunk_id, entity):
        tx.run(
            """
            MATCH (chunk:Chunk {id: $chunk_id})
            MERGE (entity:Entity {
                name: $name,
                type: $type
            })
            MERGE (chunk)-[:MENTIONS]->(entity)
            """,
            chunk_id=chunk_id,
            name=entity["text"],
            type=entity["type"]
        )
    @staticmethod
    def _create_relationship(tx, relationship):
        tx.run(
            """
            MATCH (source:Entity {
                name: $source,
                type: $source_type
            })
            MATCH (target:Entity {
                name: $target,
                type: $target_type
            })
            MERGE (source)-[:RELATED_TO]->(target)
            """,
            source=relationship["source"],
            source_type=relationship["source_type"],
            target=relationship["target"],
            target_type=relationship["target_type"]
        )