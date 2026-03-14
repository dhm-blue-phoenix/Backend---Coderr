# Third-party
from rest_framework import permissions

from ..models import Review


class IsReviewerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow reviewers of an object to edit it.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if request.method == "POST":
            return request.user.type == "customer"

        return True

    def has_object_permission(self, request, view, obj):
         if request.method in permissions.SAFE_METHODS:
            return True

        return obj.reviewer == request.user
