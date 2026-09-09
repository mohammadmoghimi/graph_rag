from elasticsearch import Elasticsearch

from knowledge.indexer import ES_URL, INDEX_NAME
from knowledge.graph import Neo4jClient
from websites.models import Website , Crawl

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

    def get_recent_activity(self, websites):
        website_ids = list(websites.values_list("id", flat=True))

        website_activity = Website.objects.filter(
            id__in=website_ids
        ).values(
            "id", "name", "created_at", "updated_at"
        )

        crawl_activity = Crawl.objects.filter(
            website_id__in=website_ids
        ).select_related("website")

        activities = []

        for website in website_activity:
            activities.append({
                "type": "website",
                "message": f"Website '{website['name']}' added",
                "created_at": website["created_at"]
            })

        for crawl in crawl_activity:
            activities.append({
                "type": "crawl",
                "message": f"Website '{crawl.website.name}' crawled",
                "created_at": crawl.completed_at or crawl.created_at
            })

        activities.sort(
            key=lambda activity: activity["created_at"],
            reverse=True
        )

        return activities[:5]
    
    def get_system_status(self):
        status = {
            "api": "online",
            "elasticsearch": "offline",
            "neo4j": "offline"
        }

        try:
            client = Elasticsearch(ES_URL)
            client.info()
            status["elasticsearch"] = "online"
            client.close()
        except Exception:
            pass

        graph = Neo4jClient()

        try:
            with graph.driver.session() as session:
                session.run("RETURN 1").single()
                status["neo4j"] = "online"
        except Exception:
            pass
        finally:
            graph.close()

        return status