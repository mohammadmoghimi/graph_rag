from rest_framework import serializers

from .models import ChatSession, ChatMessage
from websites.models import Website
from documents.models import Document


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
        write_only=True,
        required=False,
        default=[]
    )

    document_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        default=[]
    )

    websites = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            "id",
            "title",
            "website_ids",
            "document_ids",
            "websites",
            "documents",
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "websites",
            "documents",
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

    def get_documents(self, obj):
        return [
            {
                "id": document.id,
                "name": document.name,
                "description": document.description,
            }
            for document in obj.documents.all()
        ]

    def create(self, validated_data):
        website_ids = validated_data.pop("website_ids", [])
        document_ids = validated_data.pop("document_ids", [])

        user = self.context["request"].user

        websites = Website.objects.filter(
            id__in=website_ids,
            user=user,
            status="completed"
        )

        documents = Document.objects.filter(
            id__in=document_ids,
            user=user,
            status="completed"
        )

        if websites.count() != len(set(website_ids)):
            raise serializers.ValidationError(
                "You can only select your own completed websites."
            )

        if documents.count() != len(set(document_ids)):
            raise serializers.ValidationError(
                "You can only select your own completed documents."
            )

        if not website_ids and not document_ids:
            raise serializers.ValidationError(
                "Select at least one website or document."
            )

        chat = ChatSession.objects.create(
            user=user,
            **validated_data
        )

        chat.websites.set(websites)
        chat.documents.set(documents)

        return chat