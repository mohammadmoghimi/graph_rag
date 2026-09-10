from neo4j import GraphDatabase
from django.conf import settings
from rapidfuzz import process, fuzz

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
    def get_chunk_graph(self, chunk_ids, website_ids):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (website:Website)-[:HAS_CHUNK]->(chunk:Chunk)
                WHERE chunk.id IN $chunk_ids
                AND website.id IN $website_ids

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
                chunk_ids=chunk_ids,
                website_ids=website_ids
            )

            return [record.data() for record in result]
        
    def get_chunks_by_entities(self, entities, website_ids):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (website:Website)-[:HAS_CHUNK]->(chunk:Chunk)
                MATCH (chunk)-[:MENTIONS]->(entity:Entity)
                WHERE website.id IN $website_ids
                RETURN DISTINCT entity.name AS name, entity.type AS type
                """,
                website_ids=website_ids
            )

            graph_entities = [
                {"name": r["name"], "type": r["type"]}
                for r in result
            ]

        matched = []

        for entity in entities:
            candidates = [
                e for e in graph_entities
                if e["type"] == entity["type"]
            ]

            match = process.extractOne(
                entity["text"],
                [e["name"] for e in candidates],
                scorer=fuzz.ratio,
                score_cutoff=60
            )

            if match:
                matched.append(match[0])

        if not matched:
            return []

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (website:Website)-[:HAS_CHUNK]->(chunk:Chunk)
                MATCH (chunk)-[:MENTIONS]->(entity:Entity)
                WHERE website.id IN $website_ids
                AND entity.name IN $entities

                RETURN DISTINCT chunk.id AS chunk_id
                """,
                website_ids=website_ids,
                entities=matched
            )

            return [record["chunk_id"] for record in result]
        
    def get_website_graph(self, website_ids):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (website:Website)-[:HAS_CHUNK]->(chunk:Chunk)
                WHERE website.id IN $website_ids
                OPTIONAL MATCH (chunk)-[:MENTIONS]->(entity:Entity)
                OPTIONAL MATCH (entity)-[r:RELATED_TO]-(related:Entity)
                RETURN
                    entity.name AS source,
                    entity.type AS source_type,
                    type(r) AS relationship,
                    related.name AS target,
                    related.type AS target_type
            """, website_ids=website_ids)

            nodes = {}
            edges = []

            for record in result:
                if record["source"]:
                    nodes[record["source"]] = {
                        "id": record["source"],
                        "label": record["source"],
                        "type": record["source_type"]
                    }

                if record["target"]:
                    nodes[record["target"]] = {
                        "id": record["target"],
                        "label": record["target"],
                        "type": record["target_type"]
                    }

                if record["source"] and record["target"]:
                    edges.append({
                        "source": record["source"],
                        "target": record["target"],
                        "label": record["relationship"]
                    })

            return {
                "nodes": list(nodes.values()),
                "edges": edges
            }
        
    # def get_chunks_by_query(self, query, website_ids):
    #     with self.driver.session() as session:
    #         result = session.run(
    #             """
    #             MATCH (website:Website)-[:HAS_CHUNK]->(chunk:Chunk)
    #             MATCH (chunk)-[:MENTIONS]->(entity:Entity)
    #             WHERE website.id IN $website_ids
    #             RETURN DISTINCT entity.name AS name
    #             """,
    #             website_ids=website_ids
    #         )

    #         entity_names = [r["name"] for r in result]

    #     matches = process.extract(
    #         query,
    #         entity_names,
    #         scorer=fuzz.partial_ratio,
    #         limit=5,
    #         score_cutoff=60
    #     )

    #     matched_names = [match[0] for match in matches]

    #     if not matched_names:
    #         return []

    #     with self.driver.session() as session:
    #         result = session.run(
    #             """
    #             MATCH (website:Website)-[:HAS_CHUNK]->(chunk:Chunk)
    #             MATCH (chunk)-[:MENTIONS]->(entity:Entity)
    #             WHERE website.id IN $website_ids
    #             AND entity.name IN $matched_names
    #             RETURN DISTINCT chunk.id AS chunk_id
    #             """,
    #             website_ids=website_ids,
    #             matched_names=matched_names
    #         )

    #         return [r["chunk_id"] for r in result]

    def create_document_chunk(self, document_id, chunk):
        with self.driver.session() as session:
            session.execute_write(
                self._create_document_chunk,
                document_id,
                chunk
            )

    def get_chunks_by_query(self, query, website_ids, document_ids):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (chunk:Chunk)-[:MENTIONS]->(entity:Entity)

                OPTIONAL MATCH (website:Website)-[:HAS_CHUNK]->(chunk)
                OPTIONAL MATCH (document:Document)-[:HAS_CHUNK]->(chunk)

                WHERE
                    (website.id IN $website_ids)
                    OR
                    (document.id IN $document_ids)

                RETURN DISTINCT entity.name AS name
                """,
                website_ids=website_ids,
                document_ids=document_ids
            )

            entity_names = [record["name"] for record in result]

        matches = process.extract(
            query,
            entity_names,
            scorer=fuzz.partial_ratio,
            limit=5,
            score_cutoff=60
        )

        matched_names = [match[0] for match in matches]

        if not matched_names:
            return []

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (chunk:Chunk)-[:MENTIONS]->(entity:Entity)
                WHERE entity.name IN $matched_names
                AND (
                    EXISTS {
                        MATCH (website:Website)-[:HAS_CHUNK]->(chunk)
                        WHERE website.id IN $website_ids
                    }
                    OR
                    EXISTS {
                        MATCH (document:Document)-[:HAS_CHUNK]->(chunk)
                        WHERE document.id IN $document_ids
                    }
                )
                RETURN chunk.id AS chunk_id, count(entity) AS matches
                ORDER BY matches DESC
                LIMIT 5
                """,
                website_ids=website_ids,
                document_ids=document_ids,
                matched_names=matched_names
            )

            return [record["chunk_id"] for record in result]


    def get_source_graph(self, website_ids, document_ids):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (chunk:Chunk)-[:MENTIONS]->(entity:Entity)

                OPTIONAL MATCH (website:Website)-[:HAS_CHUNK]->(chunk)
                OPTIONAL MATCH (document:Document)-[:HAS_CHUNK]->(chunk)

                WHERE
                    website.id IN $website_ids
                    OR document.id IN $document_ids

                OPTIONAL MATCH (entity)-[r:RELATED_TO]-(related:Entity)

                RETURN
                    entity.name AS source,
                    entity.type AS source_type,
                    type(r) AS relationship,
                    related.name AS target,
                    related.type AS target_type
                """,
                website_ids=website_ids,
                document_ids=document_ids
            )

            nodes = {}
            edges = []

            for record in result:
                if record["source"]:
                    nodes[record["source"]] = {
                        "id": record["source"],
                        "label": record["source"],
                        "type": record["source_type"]
                    }

                if record["target"]:
                    nodes[record["target"]] = {
                        "id": record["target"],
                        "label": record["target"],
                        "type": record["target_type"]
                    }

                if record["source"] and record["target"]:
                    edges.append({
                        "source": record["source"],
                        "target": record["target"],
                        "label": record["relationship"]
                    })

            return {
                "nodes": list(nodes.values()),
                "edges": edges
            }

    @staticmethod
    def _create_document_chunk(tx, document_id, chunk):
        tx.run(
            """
            MERGE (document:Document {id: $document_id})
            MERGE (chunk:Chunk {id: $chunk_id})

            SET chunk.document_id = $document_id,
                chunk.source_file = $source_file

            MERGE (document)-[:HAS_CHUNK]->(chunk)
            """,
            document_id=document_id,
            chunk_id=chunk.metadata["chunk_id"],
            source_file=chunk.metadata["source_file"]
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