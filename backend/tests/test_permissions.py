from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.permissions import (
    HasAnyPermission,
    IsOwnerOrStaff,
    _OrgScopedPermission,
    get_user_employee_for_organization,
    user_has_permission,
)


def test_org_scoped_permission_rejects_missing_organization():
    class ConcretePermission(_OrgScopedPermission):
        def check_permission(self, request, view, organization_id):
            return True

    request = SimpleNamespace(
        user=SimpleNamespace(is_authenticated=True),
        query_params={},
    )
    assert not ConcretePermission().has_permission(request, SimpleNamespace(kwargs={}))


def test_has_any_permission_reuses_generator_on_repeated_checks():
    user = SimpleNamespace(is_authenticated=True, employees=MagicMock())
    request = SimpleNamespace(
        user=user,
        query_params={},
    )
    view = SimpleNamespace(kwargs={'organization_id': 1})
    permission = HasAnyPermission()
    permission.permission_codes = (code for code in ('orders.read',))
    assert permission.has_permission(request, view)
    assert permission.has_permission(request, view)


def test_user_has_permission_rejects_empty_code_without_query():
    user = SimpleNamespace(is_authenticated=True, employees=MagicMock())
    assert not user_has_permission(user, '')
    user.employees.filter.assert_not_called()


def test_get_user_employee_rejects_missing_organization():
    user = SimpleNamespace(is_authenticated=True, employees=MagicMock())
    assert get_user_employee_for_organization(user, None) is None
    user.employees.select_related.assert_not_called()


def test_owner_permission_accepts_created_by_id():
    user = SimpleNamespace(is_authenticated=True, is_staff=False, pk=7)
    request = SimpleNamespace(user=user)
    resource = SimpleNamespace(created_by_id=7)
    assert IsOwnerOrStaff().has_object_permission(request, None, resource)