
from urllib.parse import urlencode

from rest_framework import serializers
from rest_framework.reverse import reverse

from common.serializer_mixins import ReadOnlyMixin
from .models import (
    Product,
    Category,
    ProductImage,
    Comment,
)


class ProductImageSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for all of product images."""

    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "position"]


class ProductDetailSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for product's full details."""

    categories = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="title",
    )
    images = ProductImageSerializer(many=True, read_only=True)
    comments = serializers.HyperlinkedIdentityField(
        view_name="shop:product-comments",
        lookup_url_kwarg="product_pk",
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "title",
            "price",
            "categories",
            "description",
            "specs",
            "images",
            "comments",
        ]


class ProductListSerializer(ReadOnlyMixin,
                            serializers.HyperlinkedModelSerializer):
    """Serializer for a brief version of product;
    including a url to its individual detailed endpoint.
    """

    thumbnail = serializers.ImageField(
        source="primary_image.thumbnail",
        read_only=True,
    )

    class Meta:
        model = Product
        fields = ["id", "url", "title", "price", "thumbnail"]
        extra_kwargs = {
            "url": {"view_name": "shop:product", "lookup_field": "slug"}
        }


class CategorySerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for a category to list all the products in it."""

    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "slug", "title", "products"]

    def get_products(self, obj):
        request = self.context.get("request")
        if not request:
            return None

        url = reverse(
            "shop:category-products",
            kwargs={"category_pk": obj.pk},
            request=request,
        )

        page_num = request.query_params.get("page", None)
        if page_num and page_num.isdigit():
            return f"{url}?{urlencode({'page': page_num})}"
        return url


class CommentListSerializer(serializers.ModelSerializer):
    """Serializer for product comments."""

    class Meta:
        model = Comment
        fields = ["id", "user", "reply_to", "text", "created_at"]
        read_only_fields = ["created_at"]
