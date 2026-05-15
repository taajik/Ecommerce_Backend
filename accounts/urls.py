
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views


app_name = "accounts"

urlpatterns = [
    path("signup/",
         views.UserRegisterAPI.as_view(),
         name="signup"),
    path("login/",
         TokenObtainPairView.as_view(),
         name="login"),
    path("profile/",
         views.UserProfileAPI.as_view(),
         name="user-detail"),
    path("refresh/",
         TokenRefreshView.as_view(),
         name="refresh-token"),
    path("verify/",
         TokenVerifyView.as_view(),
         name="verify-token"),
]
