
from django.urls import path

from . import views


app_name = "shop"

urlpatterns = [
    path("product/<str:slug>/",
         views.ProductDetailAPI.as_view(),
         name="product"),
    path("category/<str:slug>/",
         views.CategoryAPI.as_view(),
         name="category"),
    path("category/<int:category_pk>/products/",
         views.CategoryProductListAPI.as_view(),
         name="category-products"),
]
