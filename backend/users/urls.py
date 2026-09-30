from rest_framework.routers import DefaultRouter

from .views import EmployeeViewSet, PermissionViewSet, RolePermissionViewSet, RoleViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'role-permissions', RolePermissionViewSet)
router.register(r'employees', EmployeeViewSet)

urlpatterns = router.urls
