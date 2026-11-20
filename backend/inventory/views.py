from decimal import Decimal

from django.db.models import Case, Count, DecimalField, ExpressionWrapper, F, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from catalog.pagination import StandardPagination
from catalog.tenant import OrganizationScopedMixin
from core.models import Branch

from .models import Inventory, InventoryTransaction
from .serializers import (AdjustmentSerializer, BranchSerializer, InventorySerializer, TransactionSerializer)
from .services import StockError, apply_stock_change, create_inventory_record

ZERO = Value(Decimal("0"), output_field=DecimalField(max_digits=16, decimal_places=2))


class BranchViewSet(OrganizationScopedMixin, viewsets.ReadOnlyModelViewSet):
    """Branch list for dropdowns. The Branch model itself belongs to the Core module."""

    serializer_class = BranchSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return Branch.objects.filter(organization=self.organization, is_active=True).order_by("-is_main_branch", "code")


class InventoryViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    pagination_class = StandardPagination
    http_method_names = ["get", "post", "patch", "head", "options"]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["product__name", "product__sku", "branch__code", "branch__name"]
    ordering_fields = ["product__name", "branch__code", "quantity", "reorder_level", "inventory_value", "updated_at"]
    ordering = ["-updated_at"]

    def base_queryset(self):
        return (
            Inventory.objects.filter(organization=self.organization)
            .select_related("product", "product__category", "branch")
            .annotate(
                inventory_value=ExpressionWrapper(
                    F("quantity") * F("product__cost_price"),
                    output_field=DecimalField(max_digits=16, decimal_places=2),
                ),
                stock_status=Case(
                    When(quantity__lte=0, then=Value("out_of_stock")),
                    When(quantity__lte=F("reorder_level"), then=Value("low_stock")),
                    default=Value("in_stock"),
                ),
            )
        )

    def get_queryset(self):
        qs = self.base_queryset()
        p = self.request.query_params
        if p.get("branch"):
            qs = qs.filter(branch_id=p["branch"])
        if p.get("product"):
            qs = qs.filter(product_id=p["product"])
        if p.get("stock_status"):
            qs = qs.filter(stock_status=p["stock_status"])
        return qs

    def _reload(self, serializer):
        serializer.instance = self.base_queryset().get(pk=serializer.instance.pk)

    def perform_create(self, serializer):
        data = serializer.validated_data
        record = create_inventory_record(
            organization=self.organization, branch=data["branch"], product=data["product"],
            quantity=data["quantity"], reorder_level=data["reorder_level"], user=self.request.user,
        )
        serializer.instance = record
        self._reload(serializer)

    def perform_update(self, serializer):
        serializer.save()
        self._reload(serializer)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        scoped = self.base_queryset()
        if request.query_params.get("branch"):
            scoped = scoped.filter(branch_id=request.query_params["branch"])
        low = Count("pk", filter=Q(stock_status="low_stock"))
        out = Count("pk", filter=Q(stock_status="out_of_stock"))
        totals = scoped.aggregate(
            total_inventory_value=Coalesce(Sum("inventory_value"), ZERO),
            total_products=Count("product", distinct=True),
            total_units=Coalesce(Sum("quantity"), 0),
            low_stock=low,
            out_of_stock=out,
        )
        totals["total_inventory_value"] = f"{totals['total_inventory_value']:.2f}"
        per_branch = {
            row["branch_id"]: row
            for row in self.base_queryset().values("branch_id").annotate(
                units=Coalesce(Sum("quantity"), 0), skus=Count("pk"), low_stock=low, out_of_stock=out
            )
        }
        branches = []
        for branch in Branch.objects.filter(organization=self.organization, is_active=True).order_by("-is_main_branch", "code"):
            row = per_branch.get(branch.pk, {})
            branches.append({
                "id": branch.pk, "code": branch.code, "name": branch.name,
                "units": row.get("units", 0), "skus": row.get("skus", 0),
                "low_stock": row.get("low_stock", 0), "out_of_stock": row.get("out_of_stock", 0),
            })
        return Response({**totals, "branches": branches})

    @action(detail=False, methods=["post"])
    def adjust(self, request):
        serializer = AdjustmentSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            record, entry = apply_stock_change(
                inventory=data["inventory"], quantity_change=data["quantity_change"],
                transaction_type=data["transaction_type"], reason=data["reason"], note=data["note"],
                reference_type=data["reference_type"], reference_id=data["reference_id"], user=request.user,
            )
        except StockError as error:
            raise ValidationError({"quantity_change": [str(error)]})
        entry = InventoryTransaction.objects.select_related("product", "branch", "created_by").get(pk=entry.pk)
        return Response(
            {
                "transaction": TransactionSerializer(entry).data,
                "inventory": InventorySerializer(self.base_queryset().get(pk=record.pk)).data,
            },
            status=201,
        )


class InventoryTransactionViewSet(OrganizationScopedMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only ledger. There is deliberately no create, update or delete endpoint."""

    serializer_class = TransactionSerializer
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["product__name", "product__sku", "reason", "reference_id"]
    ordering_fields = ["created_at", "quantity_change", "transaction_type"]
    ordering = ["-created_at", "-pk"]

    def get_queryset(self):
        qs = InventoryTransaction.objects.filter(organization=self.organization).select_related(
            "product", "branch", "created_by"
        )
        p = self.request.query_params
        for param, field in (("branch", "branch_id"), ("product", "product_id"), ("inventory", "inventory_id"),
                             ("transaction_type", "transaction_type")):
            if p.get(param):
                qs = qs.filter(**{field: p[param]})
        if p.get("date_from"):
            qs = qs.filter(created_at__date__gte=p["date_from"])
        if p.get("date_to"):
            qs = qs.filter(created_at__date__lte=p["date_to"])
        return qs