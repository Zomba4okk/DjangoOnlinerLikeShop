from rest_framework import (
    permissions,
)

from .models import (
    ORDER_STATUS_INCOMPLETE,
)


class IsOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            return obj.user_id == request.user.id
        except AttributeError:
            return False


class CanChangeOrderPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            return obj.status == ORDER_STATUS_INCOMPLETE
        except AttributeError:
            return False
