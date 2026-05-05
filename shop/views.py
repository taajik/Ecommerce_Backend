
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Product,
    Category,
)
from .serializers import (
    ProductDetailSerializer,
    CategorySerializer,
)


class ProductDetailAPI(generics.RetrieveAPIView):
    """View for an individual product instance."""

    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'


# class ProductListAPI(generics.ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductListSerializer


class CategoryAPI(generics.RetrieveAPIView):
    """View for a category and its products."""

    queryset = Category.objects.prefetch_related("products").all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
