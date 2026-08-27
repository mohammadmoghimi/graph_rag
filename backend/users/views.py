from users.models import Role, User
from users.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from .serializers import AdminUserSerializer, SignupSerializer, UserSerializer
from rest_framework.decorators import action


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
    
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return User.objects.select_related("role").all()

    @action(detail=True, methods=["post"])
    def promote(self, request, pk=None):
        user = self.get_object()

        if user == request.user:
            return Response(
                {"error": "You cannot promote yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        role, _ = Role.objects.get_or_create(
            name="admin",
            defaults={"description": "Administrator"}
        )

        user.role = role
        user.save(update_fields=["role"])

        return Response(AdminUserSerializer(user).data)