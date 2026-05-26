
from urllib.parse import urlencode

from rest_framework import serializers
from rest_framework.reverse import reverse

from common.serializer_mixins import ReadOnlyMixin
from .models import (
    Product,
    Category,
    ProductImage,
    Comment,
    Address,
    Cart,
    CartItem,
    Order,
    OrderItem,
)


class ProductImageSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for all of product images."""

    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "position"]


class ProductDetailSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for product's full details."""

    categories_list = serializers.SerializerMethodField()
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
            "categories_list",
            "description",
            "specs",
            "images",
            "comments",
        ]

    def get_categories_list(self, obj):
        return getattr(obj, "categories_list", [])


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




class CommentListSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for listing product comments."""

    user_name = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user_name", "reply_to_id", "text", "created_at"]


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating product comments."""

    class Meta:
        model = Comment
        fields = ["id", "reply_to", "text", "created_at"]
        read_only_fields = ["created_at"]

    def validate_reply_to(self, value):
        if value and value.product_id != self.context.get("product_pk"):
            raise serializers.ValidationError(
                "Reply must be on the same product."
            )
        if value and not value.is_approved:
            raise serializers.ValidationError(
                "Cannot reply to unapproved comment."
            )
        return value




class AddressSerializer(serializers.ModelSerializer):
    """Serializer for user addresses."""

    class Meta:
        model = Address
        fields = [
            "id",
            "country",
            "state",
            "city",
            "address_line",
            "postal_code",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_postal_code(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Postal code is too short.")
        return value




class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for items of the cart-product relation."""

    product = serializers.SerializerMethodField()
    quantity = serializers.IntegerField(max_value=999, min_value=1, default=1)

    class Meta:
        model = CartItem
        fields = ["product", "quantity"]

    def get_product(self, obj):
        # Simple representation without request in context,
        # doesn't need full nested object; just the id.
        request = self.context.get("request")
        if request:
            return ProductListSerializer(
                obj.product,
                context={"request": request},
            ).data
        else:
            return obj.product_id


class CartSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for user's cart."""

    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["items"]




class CheckOutSerializer(serializers.Serializer):
    """Serializer for specifying the address to use for the order."""

    address_pk = serializers.IntegerField()


class OrderItemSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for items of the order-product relation."""

    product = ProductListSerializer(read_only=True)
    quantity = serializers.IntegerField(max_value=999, min_value=1, default=1)

    class Meta:
        model = OrderItem
        fields = ["product", "price", "quantity"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["product"].pop("price", None)
        return ret


class OrderDetailSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    """Serializer for an order."""

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "items",
            "total_price",
            "shipping_address",
            "status",
            "created_at",
            "updated_at",
        ]


class OrderListSerializer(ReadOnlyMixin,
                          serializers.HyperlinkedModelSerializer):
    """Serializer for listing user orders without their items."""

    num_items = serializers.IntegerField(max_value=999, min_value=1, default=1)

    class Meta:
        model = Order
        fields = [
            "id",
            "url",
            "num_items",
            "total_price",
            "status",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "url": {"view_name": "shop:order-detail"}
        }
