from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from websites.models import Website, Crawl
from .services import DashboardService


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role.name == "admin":
            websites = Website.objects.exclude(status="deleted")
        else:
            websites = Website.objects.filter(
                user=request.user
            ).exclude(status="deleted")

        website_ids = list(websites.values_list("id", flat=True))

        crawls = Crawl.objects.filter(
            website__in=website_ids
        )

        service = DashboardService()

        return Response({
            "statistics": {
                "websites": len(website_ids),
                "crawls": crawls.count(),
                "chunks": service.get_chunk_count(website_ids),
                "entities": service.get_entity_count(website_ids),
            },
            "recent_activity": service.get_recent_activity(websites),
            "system_status": service.get_system_status(),
            "website_statistics": service.get_website_statistics(websites)
        })