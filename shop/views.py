
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Product,
)
from .serializers import (
    ProductSerializer,
)


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
