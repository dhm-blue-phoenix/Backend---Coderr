# Third-party
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsBusinessUser(BasePermission):
    """
    Permission to only allow business users to access a view.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "type", None) == "business"
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Permission to only allow the owner of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.creator == request.user
