from django.utils.text import slugify
from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    slug = serializers.SlugField(required=False)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "parent", "is_active", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate_parent(self, parent):
        if parent is not None:
            if parent.organization_id != self.context["organization"].pk:
                raise serializers.ValidationError("Invalid parent category.")
            if self.instance and parent.pk == self.instance.pk:
                raise serializers.ValidationError("A category cannot be its own parent.")
        return parent

    def validate(self, attrs):
        org = self.context["organization"]
        name = attrs.get("name", getattr(self.instance, "name", ""))
        slug = attrs.get("slug") or (getattr(self.instance, "slug", None) or slugify(name))
        clash = Category.objects.filter(organization=org, slug=slug)
        if self.instance:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError({"name": "A category with this name already exists."})
        attrs["slug"] = slug
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    stock = serializers.IntegerField(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    cost_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    selling_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)

    class Meta:
        model = Product
        fields = [
            "id", "sku", "name", "description", "unit",
            "category", "category_name",
            "cost_price", "selling_price", "reorder_level",
            "stock", "stock_status",
            "image", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_sku(self, value):
        value = value.strip().upper()
        clash = Product.objects.filter(organization=self.context["organization"], sku=value)
        if self.instance:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError("This SKU already exists in your catalog.")
        return value

    def validate_category(self, category):
        if category.organization_id != self.context["organization"].pk:
            raise serializers.ValidationError("Invalid category.")
        return category
