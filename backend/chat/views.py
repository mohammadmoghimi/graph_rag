from chat.chat_service import answer_question
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import ChatMessage, ChatSession
from .serializers import ChatSessionSerializer
from rest_framework.decorators import action
from knowledge.guardrails.prompt_guard import PromptBlockedError, PromptGuard

class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(
            user=self.request.user
        ).prefetch_related(
            "websites",
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
        
        if request.user.role and request.user.role.name != "admin":
            try:
                PromptGuard.check(question)
            except PromptBlockedError as error:
                return Response(
                    {"error": str(error)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        website_ids = list(
            chat.websites.values_list("id", flat=True)
        )

        history = list(
            chat.messages.order_by("created_at").values(
                "role",
                "content"
            )
        )

        answer = answer_question(
            question,
            website_ids,
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
            content=answer
        )

        return Response({
            "answer": answer
        })