
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination

from common.permissions import ReadOnly
from .models import (
    Product,
    Category,
    ProductImage,
    Comment,
)
from .serializers import (
    ProductDetailSerializer,
    ProductListSerializer,
    CategorySerializer,
    CommentListSerializer,
)


class ProductPagination(PageNumberPagination):
    page_size = 20


class CommentPagination(PageNumberPagination):
    page_size = 15


class ProductDetailAPI(generics.RetrieveAPIView):
    """View for an individual product instance."""

    queryset = Product.objects.prefetch_related("images").all()
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
        queryset = queryset.prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(position=0),
                to_attr="primary_images"
            )
        )
        return queryset


class ProductCommentAPI(generics.ListCreateAPIView):
    """View to create and list comments of a product."""

    serializer_class = CommentListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CommentPagination

    def get_queryset(self):
        product_pk = self.kwargs.get("product_pk")
        product = get_object_or_404(Product, pk=product_pk)
        queryset = Comment.objects.filter(product=product, is_approved=True)
        queryset = queryset.select_related("user")
        return queryset

    def perform_create(self, serializer):
        product_pk = self.kwargs.get("product_pk")
        product = get_object_or_404(Product, pk=product_pk)
        serializer.save(product=product)
