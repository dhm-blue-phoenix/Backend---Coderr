from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'type', None) == 'business')


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.creator == request.user