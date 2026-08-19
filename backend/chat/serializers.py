from rest_framework import serializers

from .models import ChatSession, ChatMessage
from websites.models import Website


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "role",
            "content",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class ChatSessionSerializer(serializers.ModelSerializer):
    website_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    websites = serializers.SerializerMethodField()
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            "id",
            "title",
            "website_ids",
            "websites",
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "websites",
            "messages",
            "created_at",
            "updated_at",
        ]

    def get_websites(self, obj):
        return [
            {
                "id": website.id,
                "name": website.name,
                "url": website.url,
            }
            for website in obj.websites.all()
        ]

    def create(self, validated_data):
        website_ids = validated_data.pop("website_ids")
        user = self.context["request"].user

        websites = Website.objects.filter(
            id__in=website_ids,
            user=user
        )

        if websites.count() != len(set(website_ids)):
            raise serializers.ValidationError(
                "You can only select your own websites."
            )

        chat = ChatSession.objects.create(
            user=user,
            **validated_data
        )

        chat.websites.set(websites)

        return chat