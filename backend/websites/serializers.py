from rest_framework import serializers
from .models import Crawl, Website


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = [
            "id",
            "name",
            "url",
            "description",
            "status",
            "created_at",
            "updated_at",
            "last_crawled_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
            "last_crawled_at",
        ]

class CrawlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crawl
        fields = [
            "id",
            "website",
            "status",
            "pages_found",
            "pages_processed",
            "error_message",
            "created_at",
            "started_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "pages_found",
            "pages_processed",
            "error_message",
            "created_at",
            "started_at",
            "completed_at",
        ]