from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsAdmin
from .models import Website
from .serializers import WebsiteSerializer


class WebsiteViewSet(viewsets.ModelViewSet):
    serializer_class = WebsiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role.name == "admin":
            return Website.objects.all()

        return Website.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)