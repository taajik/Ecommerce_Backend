
from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS,
)
from rest_framework.pagination import PageNumberPagination

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


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


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
        if category_pk is not None:
            queryset = Product.objects.filter(
                categories__pk=category_pk
            )
            queryset = queryset.prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.filter(position=0),
                    to_attr="primary_images"
                )
            )
            return queryset
        raise NotFound()


class ProductCommentAPI(generics.ListCreateAPIView):
    """View to create and list comments of a product."""

    serializer_class = CommentListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CommentPagination

    def get_queryset(self):
        product_pk = self.kwargs.get("product_pk")
        if product_pk is not None:
            return Comment.objects.filter(
                product_id=product_pk
            )
        raise NotFound()
