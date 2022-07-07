from rest_framework.permissions import SAFE_METHODS, BasePermission


class OwnerAdminReadOnly(BasePermission):
    message = ('Only for owner or admin!')

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user and request.user.is_staff
        )
