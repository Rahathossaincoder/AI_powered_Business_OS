from rest_framework import viewsets

from .models import Branch, Organization, OrganizationSetting
from .serializers import BranchSerializer, OrganizationSerializer, OrganizationSettingSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


class OrganizationSettingViewSet(viewsets.ModelViewSet):
    queryset = OrganizationSetting.objects.all()
    serializer_class = OrganizationSettingSerializer
