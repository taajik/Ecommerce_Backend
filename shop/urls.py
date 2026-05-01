
from django.urls import path

from . import views


app_name = "shop"

urlpatterns = [
    path("product/<str:slug>/",
         views.ProductDetail.as_view(),
         name="product"),
]
