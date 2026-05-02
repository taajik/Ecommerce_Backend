
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Product,
)
from .serializers import (
    ProductDetailSerializer,
    ProductListSerializer,
)


class ProductDetailAPI(generics.RetrieveAPIView):
    """View for an individual product instance."""

    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'


class ProductListAPI(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
