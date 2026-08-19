from rest_framework.routers import DefaultRouter

from .views import ChatSessionViewSet


router = DefaultRouter()
router.register("", ChatSessionViewSet, basename="chat")

urlpatterns = router.urls