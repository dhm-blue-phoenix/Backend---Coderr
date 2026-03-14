# Third-party
from rest_framework.permissions import BasePermission


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


class IsCustomer(BasePermission):
    """
    Permission to only allow customer users to access a view.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "type", None) == "customer"
        )


class IsAdmin(BasePermission):
    """
    Permission to only allow admin users to access a view.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )
