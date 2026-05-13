
from django.contrib.auth import get_user_model
from rest_framework import generics

from .serializers import UserSignupSerializer


User = get_user_model()


class UserRegisterAPI(generics.CreateAPIView):
    """View for user signup."""

    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
