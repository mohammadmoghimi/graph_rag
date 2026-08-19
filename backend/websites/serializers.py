from rest_framework import serializers
from .models import Website


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