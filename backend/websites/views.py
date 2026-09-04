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
        queryset = Website.objects.exclude(status="deleted")

        if self.request.user.role.name != "admin":
            queryset = queryset.filter(user=self.request.user)

        return queryset.order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="crawl")
    def crawl(self, request):
        serializer = WebsiteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data["url"]

        existing = Website.objects.filter(
            user=request.user,
            url=url,
            status__in=["pending", "crawling", "completed", "failed"]
        ).first()

        if existing:
            return Response(
                {"error": "این وب‌سایت قبلاً اضافه شده است."},
                status=status.HTTP_409_CONFLICT
            )

        website = serializer.save(user=request.user)

        crawl = Crawl.objects.create(
            website=website,
            status="running"
        )

        try:
            process_website(website, crawl)

            website.status = "completed"
            website.save(update_fields=["status", "updated_at"])

        except Exception as e:
            crawl.status = "failed"
            crawl.error_message = str(e)
            crawl.save()

            website.status = "failed"
            website.save(update_fields=["status", "updated_at"])

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

    def destroy(self, request, *args, **kwargs):
        website = self.get_object()

        website.status = "deleted"
        website.save(update_fields=["status", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def crawls(self, request, pk=None):
        website = self.get_object()

        crawls = website.crawls.order_by("-created_at")

        return Response(
            CrawlSerializer(crawls, many=True).data
        )
    
    def update(self, request, *args, **kwargs):
        website = self.get_object()

        if website.status != "completed":
            return Response(
                {"error": "Only successfully crawled websites can be edited."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)