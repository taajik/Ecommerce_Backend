
from django.urls import path

from . import views


app_name = "shop"

urlpatterns = [
    path("product/<int:pk>/",
         views.ProductDetail.as_view(),
         name="product"),
]
