from django.apps import apps
from rest_framework.exceptions import PermissionDenied


def get_request_organization(request):
    """The backend decides the tenant. The frontend is never trusted to send organization_id."""
    Employee = apps.get_model(
        "users", "Employee"
    )  # adjust the app label if your Employee model lives elsewhere
    employee = (
        Employee.objects.filter(user=request.user)
        .select_related("organization")
        .first()
    )
    if employee is None:
        raise PermissionDenied("Your account is not linked to an organization.")
    return employee.organization


class OrganizationScopedMixin:
    """Gives a ViewSet an `organization` property and passes it to the serializer."""

    @property
    def organization(self):
        if not hasattr(self, "_organization"):
            self._organization = get_request_organization(self.request)
        return self._organization

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.organization
        return context
