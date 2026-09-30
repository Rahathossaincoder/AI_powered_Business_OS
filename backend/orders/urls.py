from rest_framework.routers import DefaultRouter

from .views import OrderItemViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

urlpatterns = router.urls
