
from django.urls import path

from . import views


app_name = "shop"

urlpatterns = [
    path("product/<str:slug>/",
         views.ProductDetailAPI.as_view(),
         name="product"),
    # path("products/",
    #      views.ProductListAPI.as_view(),
    #      name="product-list"),
    path("category/<str:slug>/",
         views.CategoryAPI.as_view(),
         name="category"),
]
