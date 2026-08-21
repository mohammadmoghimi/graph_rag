from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from knowledge.services import process_website
from users.permissions import IsAdmin
from .models import Crawl, Website
from .serializers import CrawlSerializer, WebsiteSerializer
from rest_framework import status

class WebsiteViewSet(viewsets.ModelViewSet):
    serializer_class = WebsiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role.name == "admin":
            return Website.objects.all()

        return Website.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="crawl")
    def crawl(self, request):
        serializer = WebsiteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        website = serializer.save(user=request.user)

        crawl = Crawl.objects.create(
            website=website,
            status="running"
        )

        try:
            documents, chunks = process_website(website, crawl)

        except Exception as e:
            crawl.status = "failed"
            crawl.error_message = str(e)
            crawl.save()

            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "website": WebsiteSerializer(website).data,
                "crawl": CrawlSerializer(crawl).data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=["get"])
    def crawls(self, request, pk=None):
        website = self.get_object()

        crawls = Crawl.objects.filter(
            website=website
        ).order_by("-created_at")

        return Response(
            CrawlSerializer(crawls, many=True).data
        )