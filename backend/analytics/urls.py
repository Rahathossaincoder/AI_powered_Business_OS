from rest_framework.routers import DefaultRouter

from .views import AIConversationViewSet, AIMessageViewSet, AIToolCallViewSet

router = DefaultRouter()
router.register(r'conversations', AIConversationViewSet)
router.register(r'messages', AIMessageViewSet)
router.register(r'tool-calls', AIToolCallViewSet)

urlpatterns = router.urls
