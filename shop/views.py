
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination

from .models import (
    Product,
    Category,
)
from .serializers import (
    ProductDetailSerializer,
    CategorySerializer,
    ProductListSerializer,
)


class ProductPagination(PageNumberPagination):
    page_size = 20


class ProductDetailAPI(generics.RetrieveAPIView):
    """View for an individual product instance."""

    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"


class CategoryAPI(generics.RetrieveAPIView):
    """View for a category with a url to its products."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"


class CategoryProductListAPI(generics.ListAPIView):
    """View for listing products that are in a category."""

    serializer_class = ProductListSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        category_pk = self.kwargs.get("category_pk")
        if category_pk is not None:
            return Product.objects.filter(
                categories__pk=category_pk
            )
        raise NotFound()
