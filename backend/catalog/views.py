from django.db.models import (
    Case,
    Count,
    F,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from inventory.models import Inventory

from .models import Category, Product
from .pagination import StandardPagination
from .serializers import CategorySerializer, ProductSerializer
from .tenant import OrganizationScopedMixin


class CategoryViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    pagination_class = StandardPagination
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return Category.objects.filter(organization=self.organization).order_by("name")

    def perform_create(self, serializer):
        serializer.save(organization=self.organization)


class ProductViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "sku"]
    ordering_fields = [
        "name",
        "sku",
        "cost_price",
        "selling_price",
        "reorder_level",
        "stock",
        "created_at",
    ]
    ordering = ["-created_at"]

    def base_queryset(self):
        stock_total = (
            Inventory.objects.filter(product=OuterRef("pk"))
            .values("product")
            .annotate(total=Sum("quantity"))
            .values("total")
        )
        return (
            Product.objects.filter(organization=self.organization)
            .select_related("category")
            .annotate(
                stock=Coalesce(
                    Subquery(stock_total, output_field=IntegerField()), Value(0)
                )
            )
            .annotate(
                stock_status=Case(
                    When(stock__lte=0, then=Value("out_of_stock")),
                    When(stock__lte=F("reorder_level"), then=Value("low_stock")),
                    default=Value("in_stock"),
                )
            )
        )

    def get_queryset(self):
        qs = self.base_queryset()
        p = self.request.query_params
        if p.get("category"):
            qs = qs.filter(category_id=p["category"])
        if p.get("status") == "active":
            qs = qs.filter(is_active=True)
        elif p.get("status") == "inactive":
            qs = qs.filter(is_active=False)
        if p.get("stock_status"):
            qs = qs.filter(stock_status=p["stock_status"])
        if p.get("min_price"):
            qs = qs.filter(selling_price__gte=p["min_price"])
        if p.get("max_price"):
            qs = qs.filter(selling_price__lte=p["max_price"])
        return qs

    def _reload(self, serializer):
        serializer.instance = self.base_queryset().get(pk=serializer.instance.pk)

    def perform_create(self, serializer):
        serializer.save(organization=self.organization)
        self._reload(serializer)

    def perform_update(self, serializer):
        serializer.save()
        self._reload(serializer)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])

    @action(detail=False, methods=["get"])
    def summary(self, request):
        return Response(
            self.base_queryset().aggregate(
                total=Count("pk"),
                in_stock=Count("pk", filter=Q(stock_status="in_stock")),
                low_stock=Count("pk", filter=Q(stock_status="low_stock")),
                out_of_stock=Count("pk", filter=Q(stock_status="out_of_stock")),
            )
        )
