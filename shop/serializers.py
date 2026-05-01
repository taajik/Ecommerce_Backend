
from rest_framework import serializers

from .models import (
    Product,
)


class ReadOnlyModelSerializer(serializers.ModelSerializer):
    """A base serializer that doesn't allow creation or update."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.read_only = True

    def create(self, validated_data):
        raise serializers.ValidationError("Creation not allowed.")

    def update(self, instance, validated_data):
        raise serializers.ValidationError("Update not allowed.")


class ProductSerializer(ReadOnlyModelSerializer):
    """Serializer for product's full details."""

    class Meta:
        model = Product
        fields = ("id", "slug", "title", "price", "description", "specs")
