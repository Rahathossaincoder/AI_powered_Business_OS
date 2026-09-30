from __future__ import annotations

from typing import Iterable

from django.db.models import Q
from rest_framework.permissions import BasePermission, SAFE_METHODS


def get_user_organization_ids(user) -> set[int]:
    """Return all organization ids linked to the current user through their employees."""
    if not user or not getattr(user, 'is_authenticated', False):
        return set()

    employee_org_ids = (
        user.employees.filter(organization__isnull=False)
        .values_list('organization_id', flat=True)
        .distinct()
    )
    return set(employee_org_ids)


def get_user_employee_for_organization(user, organization_id=None):
    """Get the employee record for a user in a specific organization."""
    if not user or not getattr(user, 'is_authenticated', False):
        return None

    qs = user.employees.select_related('organization', 'role')
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    return qs.first()


def user_has_permission(user, permission_code: str, organization_id=None) -> bool:
    """Check whether a user has a specific permission code in a given organization."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False

    if organization_id is None:
        org_ids = get_user_organization_ids(user)
        if not org_ids:
            return False
        qs = user.employees.filter(organization_id__in=org_ids).select_related('role')
    else:
        qs = user.employees.filter(organization_id=organization_id).select_related('role')

    for employee in qs:
        if employee.role and employee.role.permissions.filter(permission__code=permission_code).exists():
            return True

    return False


def user_has_any_permission(user, permission_codes: Iterable[str], organization_id=None) -> bool:
    """Check whether a user has at least one permission from the given list."""
    return any(user_has_permission(user, code, organization_id) for code in permission_codes)


class IsAuthenticatedAndActive(BasePermission):
    message = 'Authentication required and account must be active.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and getattr(user, 'is_active', False))


class IsOrganizationMember(BasePermission):
    message = 'You are not a member of this organization.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False

        org_id = None
        if hasattr(request, 'data') and isinstance(request.data, dict):
            org_id = request.data.get('organization_id') or request.data.get('org_id')
        if org_id is None:
            org_id = request.query_params.get('organization_id') or request.query_params.get('org_id')
        if org_id is None and hasattr(view, 'kwargs'):
            org_id = view.kwargs.get('organization_id') or view.kwargs.get('org_id')

        if org_id is None:
            return bool(get_user_organization_ids(user))

        return user.employees.filter(organization_id=org_id).exists()


class HasPermission(BasePermission):
    """Requires the user to have a specific permission code in the organization."""
    permission_code = None
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        if not getattr(request.user, 'is_authenticated', False):
            return False

        org_id = self._get_organization_id(request, view)
        if self.permission_code is None:
            return False

        return user_has_permission(request.user, self.permission_code, org_id)

    def _get_organization_id(self, request, view):
        org_id = None

        if hasattr(request, 'data') and isinstance(request.data, dict):
            org_id = request.data.get('organization_id') or request.data.get('org_id')
        if org_id is None:
            org_id = request.query_params.get('organization_id') or request.query_params.get('org_id')
        if org_id is None and hasattr(view, 'kwargs'):
            org_id = view.kwargs.get('organization_id') or view.kwargs.get('org_id')

        return org_id


class HasAnyPermission(BasePermission):
    """Requires the user to have any of the supplied permission codes."""
    permission_codes = ()
    message = 'You do not have the required permission.'

    def has_permission(self, request, view):
        if not getattr(request.user, 'is_authenticated', False):
            return False

        org_id = self._get_organization_id(request, view)
        return user_has_any_permission(request.user, self.permission_codes, org_id)

    def _get_organization_id(self, request, view):
        org_id = None

        if hasattr(request, 'data') and isinstance(request.data, dict):
            org_id = request.data.get('organization_id') or request.data.get('org_id')
        if org_id is None:
            org_id = request.query_params.get('organization_id') or request.query_params.get('org_id')
        if org_id is None and hasattr(view, 'kwargs'):
            org_id = view.kwargs.get('organization_id') or view.kwargs.get('org_id')

        return org_id


class IsAdmin(BasePermission):
    message = 'Only admins are allowed to access this endpoint.'

    def has_permission(self, request, view):
        if not getattr(request.user, 'is_authenticated', False):
            return False

        org_id = self._get_organization_id(request, view)
        if org_id is None:
            return False

        employee = get_user_employee_for_organization(request.user, org_id)
        if not employee:
            return False

        return employee.role and employee.role.name.lower() == 'admin'

    def _get_organization_id(self, request, view):
        org_id = None
        if hasattr(request, 'data') and isinstance(request.data, dict):
            org_id = request.data.get('organization_id') or request.data.get('org_id')
        if org_id is None:
            org_id = request.query_params.get('organization_id') or request.query_params.get('org_id')
        if org_id is None and hasattr(view, 'kwargs'):
            org_id = view.kwargs.get('organization_id') or view.kwargs.get('org_id')
        return org_id


class IsManagerOrAbove(BasePermission):
    message = 'Manager-level access is required.'

    def has_permission(self, request, view):
        if not getattr(request.user, 'is_authenticated', False):
            return False

        org_id = self._get_organization_id(request, view)
        if org_id is None:
            return False

        employee = get_user_employee_for_organization(request.user, org_id)
        if not employee or not employee.role:
            return False

        role_name = employee.role.name.lower()
        return role_name in {'admin', 'manager'}

    def _get_organization_id(self, request, view):
        org_id = None
        if hasattr(request, 'data') and isinstance(request.data, dict):
            org_id = request.data.get('organization_id') or request.data.get('org_id')
        if org_id is None:
            org_id = request.query_params.get('organization_id') or request.query_params.get('org_id')
        if org_id is None and hasattr(view, 'kwargs'):
            org_id = view.kwargs.get('organization_id') or view.kwargs.get('org_id')
        return org_id


class IsReadOnly(BasePermission):
    message = 'Read-only access.'

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


__all__ = [
    'get_user_organization_ids',
    'get_user_employee_for_organization',
    'user_has_permission',
    'user_has_any_permission',
    'IsAuthenticatedAndActive',
    'IsOrganizationMember',
    'HasPermission',
    'HasAnyPermission',
    'IsAdmin',
    'IsManagerOrAbove',
    'IsReadOnly',
]
