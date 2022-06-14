# from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


class OwnerAdminReadOnly(BasePermission):
    message = ('Only for owner or admin!')

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAdminOrReadOnly(BasePermission):
    message = ('Only for admin!')

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user and request.user.is_staff
        )
