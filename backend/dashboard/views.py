from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from websites.models import Website, Crawl
from documents.models import Document
from .services import DashboardService


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role.name == "admin":
            websites = Website.objects.exclude(status="deleted")
            documents = Document.objects.exclude(status="deleted")
        else:
            websites = Website.objects.filter(
                user=request.user
            ).exclude(status="deleted")

            documents = Document.objects.filter(
                user=request.user
            ).exclude(status="deleted")

        website_ids = list(websites.values_list("id", flat=True))

        crawls = Crawl.objects.filter(
            website__in=website_ids
        )

        service = DashboardService()

        document_statistics = service.get_document_statistics(documents)

        return Response({
            "statistics": {
                "websites": len(website_ids),
                "crawls": crawls.count(),
                "completed_crawls": crawls.filter(status="completed").count(),
                "failed_crawls": crawls.filter(status="failed").count(),
                "chunks": service.get_chunk_count(website_ids),
                "entities": service.get_entity_count(website_ids),
                "documents": document_statistics["documents"],
                "completed_documents": document_statistics["completed_documents"],
                "failed_documents": document_statistics["failed_documents"],
                "processing_documents": document_statistics["processing_documents"],
                "document_chunks": document_statistics["chunks"],
                "document_entities": document_statistics["entities"],
            },
            "recent_activity": service.get_recent_activity(
                websites,
                documents
            ),
            "system_status": service.get_system_status(),
            "website_statistics": service.get_website_statistics(websites),
            "document_statistics": service.get_document_statistics_per_document(
                documents
            ),
            "crawls_per_day": service.get_crawls_per_day(websites),
        })