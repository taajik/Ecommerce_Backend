
from django.urls import path, include

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
    path("product/<int:product_pk>/comments/",
         views.ProductCommentAPI.as_view(),
         name="product-comments"),
    path("user/", include([
        path("address/",
             views.AddressAPI.as_view(),
             name="address-list"),
        path("address/<int:pk>/",
             views.AddressDetailAPI.as_view(),
             name="address-detail"),
    ]), name="user")
]
