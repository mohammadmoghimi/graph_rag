from elasticsearch import Elasticsearch

from knowledge.indexer import ES_URL, INDEX_NAME
from knowledge.graph import Neo4jClient
from websites.models import Website , Crawl
from documents.models import Document
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from chat.models import ChatSession

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

    def get_recent_activity(self, user, websites, documents):
        website_ids = list(websites.values_list("id", flat=True))
        document_ids = list(documents.values_list("id", flat=True))

        website_activity = Website.objects.filter(
            id__in=website_ids
        ).values("id", "name", "created_at")

        crawl_activity = Crawl.objects.filter(
            website_id__in=website_ids
        ).select_related("website")

        chat_activity = ChatSession.objects.filter(
            user=user
        )

        document_activity = Document.objects.filter(
            id__in=document_ids
        )

        activities = []

        for website in website_activity:
            activities.append({
                "type": "website",
                "message": f"وب‌سایت «{website['name']}» اضافه شد",
                "created_at": website["created_at"]
            })

        for crawl in crawl_activity:
            activities.append({
                "type": "crawl",
                "message": f"وب‌سایت «{crawl.website.name}» خزش شد",
                "created_at": crawl.completed_at or crawl.created_at
            })

        for document in document_activity:
            activities.append({
                "type": "document",
                "message": f"سند «{document.name}» اضافه شد",
                "created_at": document.created_at
            })

        for chat in chat_activity:
            activities.append({
                "type": "chat",
                "message": f"گفتگوی «{chat.title}» ایجاد شد",
                "created_at": chat.created_at
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
    
    def get_website_statistics(self, websites):
        website_ids = list(websites.values_list("id", flat=True))

        if not website_ids:
            return []

        graph = Neo4jClient()

        try:
            client = Elasticsearch(ES_URL)

            response = client.search(
                index=INDEX_NAME,
                size=0,
                query={
                    "terms": {
                        "metadata.website_id": website_ids
                    }
                },
                aggs={
                    "websites": {
                        "terms": {
                            "field": "metadata.website_id",
                            "size": len(website_ids)
                        }
                    }
                }
            )

            chunk_counts = {
                bucket["key"]: bucket["doc_count"]
                for bucket in response["aggregations"]["websites"]["buckets"]
            }

            client.close()

            result = []

            for website in websites:
                crawl_data = Crawl.objects.filter(
                    website=website,
                    
                ).order_by("completed_at")

                last_crawl = crawl_data.first()

                with graph.driver.session() as session:
                    entity_result = session.run(
                        """
                        MATCH (website:Website)-[:HAS_CHUNK]->(:Chunk)-[:MENTIONS]->(entity:Entity)
                        WHERE website.id = $website_id
                        RETURN count(DISTINCT entity) AS count
                        """,
                        website_id=website.id
                    )

                    entity_count = entity_result.single()["count"]

                result.append({
                    "id": website.id,
                    "name": website.name,
                    "crawls": crawl_data.count(),
                    "pages": sum(c.pages_processed for c in crawl_data),
                    "chunks": chunk_counts.get(website.id, 0),
                    "entities": entity_count,
                    "last_crawled_at": last_crawl.completed_at if last_crawl else None,
                    "status": website.status
                })

            return result

        finally:
            graph.close()

    def get_crawls_per_day(self, websites):
        start_date = timezone.now().date() - timedelta(days=6)

        crawls = (
            Crawl.objects
            .filter(
                website__in=websites,
                created_at__date__gte=start_date
            )
            .values("created_at__date")
            .annotate(count=Count("id"))
            .order_by("created_at__date")
        )

        counts = {
            item["created_at__date"]: item["count"]
            for item in crawls
        }

        return [
            {
                "date": start_date + timedelta(days=i),
                "count": counts.get(start_date + timedelta(days=i), 0)
            }
            for i in range(7)
        ]
    
    def get_document_statistics(self, documents):
        document_ids = list(documents.values_list("id", flat=True))

        if not document_ids:
            return {
                "documents": 0,
                "completed_documents": 0,
                "failed_documents": 0,
                "processing_documents": 0,
                "chunks": 0,
                "entities": 0
            }

        client = Elasticsearch(ES_URL)

        response = client.count(
            index=INDEX_NAME,
            query={
                "terms": {
                    "metadata.document_id": document_ids
                }
            }
        )

        chunk_count = response["count"]
        client.close()

        graph = Neo4jClient()

        try:
            with graph.driver.session() as session:
                result = session.run(
                    """
                    MATCH (document:Document)-[:HAS_CHUNK]->(:Chunk)-[:MENTIONS]->(entity:Entity)
                    WHERE document.id IN $document_ids
                    RETURN count(DISTINCT entity) AS count
                    """,
                    document_ids=document_ids
                )

                entity_count = result.single()["count"]
        finally:
            graph.close()

        return {
            "documents": len(document_ids),
            "completed_documents": documents.filter(status="completed").count(),
            "failed_documents": documents.filter(status="failed").count(),
            "processing_documents": documents.filter(
                status="processing"
            ).count(),
            "chunks": chunk_count,
            "entities": entity_count
        }
    
    def get_document_statistics_per_document(self, documents):
        document_ids = list(documents.values_list("id", flat=True))

        if not document_ids:
            return []

        client = Elasticsearch(ES_URL)

        response = client.search(
            index=INDEX_NAME,
            size=0,
            query={
                "terms": {
                    "metadata.document_id": document_ids
                }
            },
            aggs={
                "documents": {
                    "terms": {
                        "field": "metadata.document_id",
                        "size": len(document_ids)
                    }
                }
            }
        )

        chunk_counts = {
            bucket["key"]: bucket["doc_count"]
            for bucket in response["aggregations"]["documents"]["buckets"]
        }

        client.close()

        result = []

        for document in documents:
            result.append({
                "id": document.id,
                "name": document.name,
                "chunks": chunk_counts.get(document.id, 0),
                "status": document.status,
                "created_at": document.created_at,
                "updated_at": document.updated_at
            })

        return result