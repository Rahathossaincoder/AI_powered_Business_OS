from rest_framework.routers import DefaultRouter

from .views import InvoiceViewSet, PaymentViewSet, ReceiptViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'receipts', ReceiptViewSet)

urlpatterns = router.urls
