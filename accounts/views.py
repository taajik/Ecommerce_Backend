
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsOwnUser
from .serializers import (
    UserSignupSerializer,
    UserDetailSerializer,
)


User = get_user_model()


class UserRegisterAPI(generics.CreateAPIView):
    """View for user signup."""

    queryset = User.objects.all()
    serializer_class = UserSignupSerializer


class UserProfileAPI(generics.RetrieveUpdateAPIView):
    """View for a user's details."""

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnUser]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj
