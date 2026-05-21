
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import generics
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
)
from .serializers import (
    ProductDetailSerializer,
    ProductListSerializer,
    CategorySerializer,
    CommentListSerializer,
    CommentCreateSerializer,
    AddressSerializer,
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

    def get_product(self):
        if not hasattr(self, "_product"):
            product_pk = self.kwargs.get("product_pk")
            self._product = get_object_or_404(Product, pk=product_pk)
        return self._product


class AddressAPI(generics.ListCreateAPIView):
    """View to create and list addresses for a user."""

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsOwner]
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
