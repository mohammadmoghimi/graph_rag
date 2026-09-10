from knowledge.graph import Neo4jClient
from chat.chat_service import answer_question
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import ChatMessage, ChatSession
from .serializers import ChatSessionSerializer
from rest_framework.decorators import action
from knowledge.guardrail_service import guardrail_service
from documents.models import Document

class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(
            user=self.request.user
        ).prefetch_related(
            "websites",
            "documents",
            "messages"
        )

    @action(detail=True, methods=["post"])
    def ask(self, request, pk=None):
        chat = self.get_object()

        question = request.data.get("question")

        if not question:
            return Response(
                {"error": "Question is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.user.role.name != "admin":
            if not guardrail_service.is_allowed(question):
                return Response(
                    {"error": "این درخواست مجاز نیست."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        website_ids = list(
            chat.websites.values_list("id", flat=True)
        )

        document_ids = list(
            chat.documents.values_list("id", flat=True)
        )

        history = list(
            chat.messages.order_by("created_at").values(
                "role",
                "content"
            )
        )

        result = answer_question(
            question,
            website_ids,
            document_ids,
            history
        )

        ChatMessage.objects.create(
            chat_session=chat,
            role="user",
            content=question
        )

        ChatMessage.objects.create(
            chat_session=chat,
            role="assistant",
            content=result["answer"]
        )

        return Response(result)
    
    @action(detail=True, methods=["get"])
    def graph(self, request, pk=None):
        chat = self.get_object()

        website_ids = list(
            chat.websites.values_list("id", flat=True)
        )

        document_ids = list(
            chat.documents.values_list("id", flat=True)
        )

        neo4j_client = Neo4jClient()

        try:
            graph = neo4j_client.get_source_graph(
                website_ids,
                document_ids
            )
        finally:
            neo4j_client.close()

        return Response(graph)