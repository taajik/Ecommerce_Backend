
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
    SAFE_METHODS,
)


class ReadOnly(BasePermission):
    """Permission to only allow safe methods."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsOwnUser(IsAuthenticated):
    """Permission to only allow a user to access their own user object."""

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwner(BasePermission):
    """Permission to only allow owners of an object to view/edit it."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False


class IsOwnerOrReadOnly(IsOwner):
    """Permission to allow unsafe methods only for owners of an object."""

    def has_object_permission(self, request, view, obj):
        is_owner = super().has_object_permission(request, view, obj)
        if not is_owner and request.method not in SAFE_METHODS:
            return False
        return True
