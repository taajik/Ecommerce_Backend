
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""

    password = serializers.CharField(max_length=128, write_only=True,
                                     validators=[validate_password])
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords don't match.")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user details."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "created_at",
            # "addresses",
            # "cart",
            # "orders",
        ]
        read_only_fields = ["email", "created_at"]

    def create(self, validated_data):
        raise serializers.ValidationError(
            "Creating users through this endpoint is not allowed. "
            "Please use the signup endpoint."
        )
