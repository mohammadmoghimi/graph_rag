from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Document
from .serializers import DocumentSerializer
from .services import process_document


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Document.objects.exclude(status="deleted")

        if self.request.user.role.name != "admin":
            queryset = queryset.filter(user=self.request.user)

        return queryset.order_by("-id")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        serializer = DocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response(
                {"error": "File is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        document = serializer.save(user=request.user)

        try:
            process_document(document, uploaded_file)

        except Exception as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )