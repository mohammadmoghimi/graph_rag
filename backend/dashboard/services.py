from elasticsearch import Elasticsearch

from knowledge.indexer import ES_URL, INDEX_NAME
from knowledge.graph import Neo4jClient


class DashboardService:

    def get_chunk_count(self, website_ids):
        if not website_ids:
            return 0

        client = Elasticsearch(ES_URL)

        response = client.count(
            index=INDEX_NAME,
            query={
                "terms": {
                    "metadata.website_id": website_ids
                }
            }
        )

        client.close()

        return response["count"]

    def get_entity_count(self, website_ids):
        if not website_ids:
            return 0

        graph = Neo4jClient()

        try:
            with graph.driver.session() as session:
                result = session.run(
                    """
                    MATCH (website:Website)-[:HAS_CHUNK]->(:Chunk)-[:MENTIONS]->(entity:Entity)
                    WHERE website.id IN $website_ids
                    RETURN count(DISTINCT entity) AS count
                    """,
                    website_ids=website_ids
                )

                return result.single()["count"]
        finally:
            graph.close()