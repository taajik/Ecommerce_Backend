
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserDetailSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


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
