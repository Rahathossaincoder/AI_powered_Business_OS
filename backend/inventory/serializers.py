from rest_framework import serializers

from catalog.models import Product
from core.models import Branch

from .models import Inventory, InventoryTransaction, TransactionType
from .services import StockError, check_change


class BranchSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)

    class Meta:
        model = Branch
        fields = ["id", "code", "name", "is_main_branch"]


class InventorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)
    unit = serializers.CharField(source="product.unit", read_only=True)
    category_name = serializers.CharField(source="product.category.name", read_only=True)
    branch_code = serializers.CharField(source="branch.code", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    unit_cost = serializers.DecimalField(source="product.cost_price", max_digits=12, decimal_places=2, read_only=True)
    inventory_value = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)
    stock_status = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(min_value=0, required=False, default=0)
    reorder_level = serializers.IntegerField(min_value=0, required=False, default=0)

    class Meta:
        model = Inventory
        fields = [
            "id", "branch", "branch_code", "branch_name", "product", "product_name", "sku", "unit",
            "category_name", "quantity", "reorder_level", "stock_status", "unit_cost", "inventory_value",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]
        validators = []  # branch+product uniqueness is checked in validate() for a clearer message

    def validate_branch(self, branch):
        if branch.organization_id != self.context["organization"].pk:
            raise serializers.ValidationError("Invalid branch.")
        return branch

    def validate_product(self, product):
        if product.organization_id != self.context["organization"].pk:
            raise serializers.ValidationError("Invalid product.")
        return product

    def validate(self, attrs):
        if self.instance is not None:
            if "quantity" in attrs and attrs["quantity"] != self.instance.quantity:
                raise serializers.ValidationError({"quantity": "Use a stock adjustment to change quantity."})
            for field in ("branch", "product"):
                if field in attrs and attrs[field] != getattr(self.instance, field):
                    raise serializers.ValidationError({field: "Cannot be changed. Create a new record instead."})
            return attrs
        clash = Inventory.objects.filter(branch=attrs["branch"], product=attrs["product"])
        if clash.exists():
            raise serializers.ValidationError({"product": "This product already has a stock record at this branch."})
        return attrs


class AdjustmentSerializer(serializers.Serializer):
    inventory = serializers.PrimaryKeyRelatedField(queryset=Inventory.objects.all())
    transaction_type = serializers.ChoiceField(choices=TransactionType.choices)
    quantity_change = serializers.IntegerField()
    reason = serializers.CharField(max_length=100)
    note = serializers.CharField(required=False, allow_blank=True, default="")
    reference_type = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    reference_id = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")

    def validate_inventory(self, inventory):
        if inventory.organization_id != self.context["organization"].pk:
            raise serializers.ValidationError("Invalid inventory record.")
        return inventory

    def validate(self, attrs):
        try:
            check_change(attrs["transaction_type"], attrs["quantity_change"], attrs["inventory"].quantity)
        except StockError as error:
            raise serializers.ValidationError({"quantity_change": str(error)})
        return attrs


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)
    branch_code = serializers.CharField(source="branch.code", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = InventoryTransaction
        fields = [
            "id", "created_at", "inventory", "product", "product_name", "sku", "branch", "branch_code",
            "branch_name", "transaction_type", "quantity_change", "quantity_before", "quantity_after",
            "reference_type", "reference_id", "reason", "note", "created_by_name",
        ]
        read_only_fields = fields

    def get_created_by_name(self, obj):
        user = obj.created_by
        if user is None:
            return "System"
        return user.get_full_name() or getattr(user, "email", "") or user.get_username()