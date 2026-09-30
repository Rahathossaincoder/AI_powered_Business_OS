from rest_framework.routers import DefaultRouter

from .views import BranchViewSet, OrganizationSettingViewSet, OrganizationViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'branches', BranchViewSet)
router.register(r'organization-settings', OrganizationSettingViewSet)

urlpatterns = router.urls
