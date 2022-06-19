from rest_framework.permissions import BasePermission, SAFE_METHODS


class OwnerAdminReadOnly(BasePermission):
    message = ('Only for owner or admin!')

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )


class IsAdminOrReadOnly(BasePermission):
    message = ('Only for admin!')

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user and request.user.is_staff
        )
