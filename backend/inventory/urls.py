from rest_framework.routers import DefaultRouter

from .views import InventoryTransactionViewSet, InventoryViewSet

router = DefaultRouter()
router.register(r'inventory', InventoryViewSet)
router.register(r'inventory-transactions', InventoryTransactionViewSet)

urlpatterns = router.urls
