from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from users.permissions import IsAdmin
from .models import Crawl, Website
from .serializers import CrawlSerializer, WebsiteSerializer


class WebsiteViewSet(viewsets.ModelViewSet):
    serializer_class = WebsiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role.name == "admin":
            return Website.objects.all()

        return Website.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def crawl(self, request, pk=None):
        website = self.get_object()

        crawl = Crawl.objects.create(
            website=website,
            status="pending"
        )

        website.status = "pending"
        website.save(update_fields=["status"])

        return Response(
            CrawlSerializer(crawl).data,
            status=201
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