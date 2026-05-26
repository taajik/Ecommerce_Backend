
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.db.models import Prefetch
from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.pagination import PageNumberPagination

from common.permissions import IsOwner, ReadOnly
from .models import (
    Product,
    Category,
    Comment,
    Address,
    Cart,
    CartItem,
    Order,
    OrderItem,
)
from .serializers import (
    ProductDetailSerializer,
    ProductListSerializer,
    CategorySerializer,
    CommentListSerializer,
    CommentCreateSerializer,
    AddressSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    CheckOutSerializer,
)


class ProductPagination(PageNumberPagination):
    page_size = 20


class CommentPagination(PageNumberPagination):
    page_size = 15




class ProductDetailAPI(generics.RetrieveAPIView):
    """View for an individual product instance."""

    queryset = Product.objects.annotate(
        categories_list=ArrayAgg("categories__title")
    ).prefetch_related("images")
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
    permission_classes = [ReadOnly]


class CategoryAPI(generics.RetrieveAPIView):
    """View for a category with a url to its products."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [ReadOnly]


class CategoryProductListAPI(generics.ListAPIView):
    """View for listing products that are in a category."""

    serializer_class = ProductListSerializer
    permission_classes = [ReadOnly]
    pagination_class = ProductPagination

    def get_queryset(self):
        category_pk = self.kwargs.get("category_pk")
        category = get_object_or_404(Category, pk=category_pk)
        queryset = Product.objects.filter(categories=category)
        queryset = queryset.select_related("primary_image")
        return queryset




class ProductCommentAPI(generics.ListCreateAPIView):
    """View to create and list comments of a product."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CommentPagination

    def get_product(self):
        if not hasattr(self, "_product"):
            product_pk = self.kwargs.get("product_pk")
            self._product = get_object_or_404(Product, pk=product_pk)
        return self._product

    def get_queryset(self):
        queryset = Comment.objects.filter(
            product=self.get_product(),
            is_approved=True,
        )
        queryset = queryset.annotate(user_name=F("user__email"))
        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["product_pk"] = self.kwargs.get("product_pk")
        return context

    def perform_create(self, serializer):
        serializer.save(
            product=self.get_product(),
            user=self.request.user,
        )




class AddressAPI(generics.ListCreateAPIView):
    """View to create and list addresses for a user."""

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """View to edit a user address."""

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)




class CartAPI(generics.RetrieveAPIView):
    """View to list products in a user's cart."""

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, created = Cart.objects.prefetch_related(
            Prefetch(
                "items",
                queryset=CartItem.objects.select_related("product"),
            )
        ).get_or_create(user=self.request.user)
        return cart


class CartItemAPI(APIView):
    """View to add, update, or delete an item in the cart."""

    permission_classes = [IsAuthenticated]

    def get_cart(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @transaction.atomic
    def post(self, request, product_pk=None):
        """Add item to cart."""
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.get_cart()
        product = get_object_or_404(Product, id=product_pk)
        quantity = serializer.validated_data.get("quantity", 1)
        if product.stock < quantity:
            raise ValidationError("Insufficient stock.")

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity}
        )
        if not created and quantity != cart_item.quantity:
            cart_item.quantity = quantity
            cart_item.save()

        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED if created
            else status.HTTP_200_OK
        )

    def put(self, request, product_pk=None):
        """Update item quantity in cart."""
        return self._update_quantity(request, product_pk)

    def patch(self, request, product_pk=None):
        """Update item quantity in cart."""
        return self._update_quantity(request, product_pk)

    def _update_quantity(self, request, product_pk):
        cart = self.get_cart()
        cart_item = get_object_or_404(CartItem, cart=cart,
                                      product_id=product_pk)

        serializer = CartItemSerializer(cart_item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, product_pk=None):
        """Remove item from cart."""
        cart = self.get_cart()
        cart_item = get_object_or_404(CartItem, cart=cart,
                                      product_id=product_pk)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class OrderAPI(APIView):
    """View to create orders for a user."""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        """Check out all products in the cart as an order."""
        serializer = CheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address_pk = serializer.validated_data.get("address_pk")
        address = get_object_or_404(Address, id=address_pk, user=request.user)
        cart = get_object_or_404(Cart.objects.prefetch_related(
            Prefetch(
                "items",
                queryset=CartItem.objects.select_related("product"),
            )
        ), user=request.user)
        cart_items = list(cart.items.all())

        if not cart_items:
            return Response(
                {"error": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.create(
            user=request.user,
            shipping_address=address.get_full_address(),
            status=Order.PENDING
        )

        total_price = Decimal("0.00")
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity,
            )
            total_price += item.product.price * item.quantity
        order.total_price = total_price
        order.save()
        CartItem.objects.filter(cart=cart).delete()

        return Response(
            OrderSerializer(order, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )


class OrderDetailAPI(generics.RetrieveAPIView):
    """View for each order's details."""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        queryset = queryset.prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product"),
            )
        )
        return queryset
