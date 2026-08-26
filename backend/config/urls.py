from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import CurrentUserView, SignupView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/websites/", include("websites.urls")),
    path("api/auth/login/", TokenObtainPairView.as_view()),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("api/auth/me/", CurrentUserView.as_view()),
    path("api/chats/", include("chat.urls")),
    path("api/auth/signup/", SignupView.as_view()),
]
