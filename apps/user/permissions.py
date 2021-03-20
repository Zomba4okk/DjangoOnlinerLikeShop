from rest_framework.permissions import BasePermission

from .models import (
    ACCOUNT_TYPE_MODERATOR,
    ACCOUNT_TYPE_ADMIN,
)


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.account_type == ACCOUNT_TYPE_MODERATOR


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.account_type == ACCOUNT_TYPE_ADMIN
