from __future__ import annotations

from typing import Any, Iterable

from rest_framework.permissions import BasePermission, SAFE_METHODS


# ==== Shared helpers ====

def _is_authenticated(user: Any) -> bool:
    """Return whether a user object represents an authenticated account."""
    return bool(user and getattr(user, 'is_authenticated', False))


def _is_support(user: Any) -> bool:
    """Return whether a user is a support agent or Django staff member."""
    return bool(
        getattr(user, 'is_support_agent', False)
        or getattr(user, 'is_staff', False)
    )


def _resolve_org_id(request: Any, view: Any) -> int | None:
    """Resolve an organization id from route context before query parameters."""
    kwargs = getattr(view, 'kwargs', {}) or {}
    if 'organization_id' in kwargs:
        raw_org_id = kwargs['organization_id']
    elif 'org_id' in kwargs:
        raw_org_id = kwargs['org_id']
    else:
        query_params = getattr(request, 'query_params', {})
        if 'organization_id' in query_params:
            raw_org_id = query_params['organization_id']
        else:
            raw_org_id = query_params.get('org_id')

    try:
        return int(raw_org_id) if raw_org_id is not None else None
    except (TypeError, ValueError):
        return None


def _role_name(employee: Any) -> str:
    """Normalize an employee role name for consistent role-based checks."""
    if not employee or not employee.role:
        return ''
    return (employee.role.name or '').strip().lower()


# ==== Query helpers ====

def get_user_organization_ids(user: Any) -> set[int]:
    """Return organization ids linked to an authenticated user."""
    if not _is_authenticated(user):
        return set()

    employee_org_ids = (
        user.employees.filter(organization__isnull=False)
        .values_list('organization_id', flat=True)
        .distinct()
    )
    return set(employee_org_ids)


def get_user_employee_for_organization(
    user: Any,
    organization_id: int | None,
) -> Any:
    """Return a user's employee record only within the requested organization."""
    if not _is_authenticated(user) or organization_id is None:
        return None
    try:
        organization_id = int(organization_id)
    except (TypeError, ValueError):
        return None

    return (
        user.employees.select_related('organization', 'role')
        .filter(organization_id=organization_id)
        .first()
    )


def user_has_permission(
    user: Any,
    permission_code: str,
    organization_id: int | None = None,
) -> bool:
    """Check one role permission with a single database existence query."""
    if not _is_authenticated(user) or not permission_code:
        return False

    employees = user.employees.filter(organization__isnull=False)
    if organization_id is not None:
        employees = employees.filter(organization_id=organization_id)

    return employees.filter(
        role__permissions__permission__code=permission_code,
    ).exists()


def user_has_any_permission(
    user: Any,
    permission_codes: Iterable[str],
    organization_id: int | None = None,
) -> bool:
    """Check several role permissions with one database existence query."""
    if not _is_authenticated(user):
        return False

    codes = tuple(permission_codes)
    if not codes:
        return False

    employees = user.employees.filter(organization__isnull=False)
    if organization_id is not None:
        employees = employees.filter(organization_id=organization_id)

    return employees.filter(
        role__permissions__permission__code__in=codes,
    ).exists()


# ==== Permission logic ====

class IsAuthenticatedAndActive(BasePermission):
    """Allow access only to authenticated users with active accounts."""

    message = 'Authentication required and account must be active.'

    def has_permission(self, request: Any, view: Any) -> bool:
        """Reject anonymous or disabled users before a view is executed."""
        user = getattr(request, 'user', None)
        return _is_authenticated(user) and bool(getattr(user, 'is_active', False))


class IsOrganizationMember(BasePermission):
    """Allow users linked to the requested organization, or any organization."""

    message = 'You are not a member of this organization.'

    def has_permission(self, request: Any, view: Any) -> bool:
        """Use route/query context without allowing request bodies to select an org."""
        user = getattr(request, 'user', None)
        if not _is_authenticated(user):
            return False

        organization_id = _resolve_org_id(request, view)
        if organization_id is None:
            return bool(get_user_organization_ids(user))

        return user.employees.filter(organization_id=organization_id).exists()


# ==== Base classes ====

class _OrgScopedPermission(BasePermission):
    """Resolve the organization once before delegating an org-scoped decision."""

    allow_missing_organization: bool = False
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request: Any, view: Any) -> bool:
        """Pass the URL/query organization id to the concrete permission check."""
        if not _is_authenticated(getattr(request, 'user', None)):
            return False

        organization_id = _resolve_org_id(request, view)
        if organization_id is None and not self.allow_missing_organization:
            return False
        return self.check_permission(request, view, organization_id)

    def check_permission(
        self,
        request: Any,
        view: Any,
        organization_id: int | None,
    ) -> bool:
        """Decide access for a resolved organization; subclasses provide the rule."""
        raise NotImplementedError


# ==== Org-scoped permissions ====

class HasPermission(_OrgScopedPermission):
    """Require one configured permission code in the resolved organization."""

    allow_missing_organization = False
    permission_code: str | None = None
    message = 'You do not have permission to perform this action.'

    def check_permission(
        self,
        request: Any,
        view: Any,
        organization_id: int | None,
    ) -> bool:
        """Check the configured code while preserving all-organization fallback."""
        if self.permission_code is None:
            return False
        return user_has_permission(
            request.user,
            self.permission_code,
            organization_id,
        )


class HasAnyPermission(_OrgScopedPermission):
    """Require a configured permission code in the resolved organization."""

    allow_missing_organization = False
    permission_codes: Iterable[str] = ()
    message = 'You do not have the required permission.'

    def check_permission(
        self,
        request: Any,
        view: Any,
        organization_id: int | None,
    ) -> bool:
        """Check all configured codes through one organization-scoped query."""
        codes = tuple(self.permission_codes or ())
        if not codes:
            return False
        self.permission_codes = codes
        return user_has_any_permission(
            request.user,
            codes,
            organization_id,
        )


class IsAdmin(_OrgScopedPermission):
    """Allow users with an admin employee role in the resolved organization."""

    message = 'Only admins are allowed to access this endpoint.'

    def check_permission(
        self,
        request: Any,
        view: Any,
        organization_id: int | None,
    ) -> bool:
        """Require an explicit organization so a role cannot come from elsewhere."""
        if organization_id is None:
            return False
        employee = get_user_employee_for_organization(request.user, organization_id)
        return _role_name(employee) == 'admin'


class IsManagerOrAbove(_OrgScopedPermission):
    """Allow users with manager-level or admin employee roles."""

    message = 'Manager-level access is required.'

    def check_permission(
        self,
        request: Any,
        view: Any,
        organization_id: int | None,
    ) -> bool:
        """Require an explicit organization before checking the employee role."""
        if organization_id is None:
            return False
        employee = get_user_employee_for_organization(request.user, organization_id)
        return _role_name(employee) in {'admin', 'manager'}


# ==== Role-flag permissions ====

class IsReadOnly(BasePermission):
    """Allow only safe HTTP methods for endpoints that must not mutate data."""

    message = 'Read-only access.'

    def has_permission(self, request: Any, view: Any) -> bool:
        """Permit methods that do not modify server-side resources."""
        return request.method in SAFE_METHODS


class IsCustomerUser(BasePermission):
    """Allow authenticated accounts explicitly marked as customers."""

    message = 'Customer account required.'

    def has_permission(self, request: Any, view: Any) -> bool:
        """Require the customer flag instead of treating staff as customers."""
        user = getattr(request, 'user', None)
        return _is_authenticated(user) and bool(getattr(user, 'is_customer', False))


class IsSupportAgentUser(BasePermission):
    """Allow authenticated support agents or Django staff members."""

    message = 'Support agent account required.'

    def has_permission(self, request: Any, view: Any) -> bool:
        """Apply the shared support predicate consistently across endpoints."""
        user = getattr(request, 'user', None)
        return _is_authenticated(user) and _is_support(user)


class IsOwnerOrStaff(BasePermission):
    """Allow owners and support staff; list views must scope their querysets."""

    message = 'You can only access your own resources.'

    def has_permission(self, request: Any, view: Any) -> bool:
        """Require authentication before object-level ownership checks run."""
        return _is_authenticated(getattr(request, 'user', None))

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        """Check raw owner ids; list endpoints must scope get_queryset themselves."""
        if _is_support(request.user):
            return True

        owner_id = getattr(obj, 'user_id', None)
        if owner_id is None:
            owner_id = getattr(obj, 'created_by_id', None)

        return owner_id is not None and owner_id == request.user.pk


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
    'IsCustomerUser',
    'IsSupportAgentUser',
    'IsOwnerOrStaff',
]