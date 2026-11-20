from rest_framework.routers import DefaultRouter

from .views import BranchViewSet, InventoryTransactionViewSet, InventoryViewSet

router = DefaultRouter()
router.register("inventory", InventoryViewSet, basename="inventory")
router.register("inventory-transactions", InventoryTransactionViewSet, basename="inventory-transaction")
router.register("branches", BranchViewSet, basename="branch")

urlpatterns = router.urls