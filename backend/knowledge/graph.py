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

    def get_graph_data(self):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (entity:Entity)
                OPTIONAL MATCH (entity)-[:RELATED_TO]-(related:Entity)
                RETURN
                    entity.name AS name,
                    entity.type AS type,
                    collect(DISTINCT related.name) AS related
                """
            )

            entities = []
            relationships = []

            for record in result:
                entity = {
                    "text": record["name"],
                    "type": record["type"]
                }

                entities.append(entity)

                for related in record["related"]:
                    if related:
                        relationships.append({
                            "source": record["name"],
                            "target": related
                        })

            return entities, relationships
        
    def create_community(self, community_id, entities, summary):
        with self.driver.session() as session:
            session.execute_write(
                self._create_community,
                community_id,
                entities,
                summary
            )
    def get_chunk_graph(self, chunk_ids):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (chunk:Chunk)
                WHERE chunk.id IN $chunk_ids

                OPTIONAL MATCH (chunk)-[:MENTIONS]->(entity:Entity)

                OPTIONAL MATCH (entity)-[:RELATED_TO]-(related:Entity)

                OPTIONAL MATCH (entity)-[:BELONGS_TO]->(community:Community)

                RETURN
                    chunk.id AS chunk_id,
                    collect(DISTINCT {
                        name: entity.name,
                        type: entity.type
                    }) AS entities,
                    collect(DISTINCT {
                        name: related.name,
                        type: related.type
                    }) AS related_entities,
                    collect(DISTINCT {
                        id: community.id,
                        summary: community.summary
                    }) AS communities
                """,
                chunk_ids=chunk_ids
            )

            return [record.data() for record in result]


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
    @staticmethod
    def _create_community(tx, community_id, entities, summary):
        tx.run(
            """
            MERGE (community:Community {id: $community_id})
            SET community.summary = $summary

            WITH community
            UNWIND $entities AS entity
            MATCH (e:Entity {name: entity.text, type: entity.type})
            MERGE (e)-[:BELONGS_TO]->(community)
            """,
            community_id=community_id,
            entities=entities,
            summary=summary
        )