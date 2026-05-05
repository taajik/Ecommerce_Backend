
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from .models import (
    Product,
    Category,
)


class ReadOnlyMixin:
    """Mark all fields read-only and disallow creation or update."""

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields

    def create(self, validated_data):
        raise MethodNotAllowed("POST", detail="Creation not allowed.")

    def update(self, instance, validated_data):
        raise MethodNotAllowed("PUT", detail="Update not allowed.")


class ProductDetailSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for product's full details."""

    class Meta:
        model = Product
        fields = ["id", "slug", "title", "price", "description", "specs"]


class ProductListSerializer(ReadOnlyMixin,
                            serializers.HyperlinkedModelSerializer):
    """Serializer for a brief version of product;
    including a url to its individual detailed endpoint.
    """

    class Meta:
        model = Product
        fields = ["url", "id", "title", "price"]
        extra_kwargs = {
            'url': {'view_name': 'shop:product', 'lookup_field': 'slug'}
        }


class CategorySerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for a category to list all the products in it."""

    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "slug", "title", "products"]
