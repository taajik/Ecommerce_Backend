
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import BasePermission, IsAuthenticated

from .serializers import (
    UserSignupSerializer,
    UserDetailSerializer,
)


User = get_user_model()


class IsUserOwner(BasePermission):
    """Permission to only allow a user to access their own user object."""

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class UserRegisterAPI(generics.CreateAPIView):
    """View for user signup."""

    queryset = User.objects.all()
    serializer_class = UserSignupSerializer


class UserProfileAPI(generics.RetrieveUpdateAPIView):
    """View for a user's details."""

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, IsUserOwner]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj
