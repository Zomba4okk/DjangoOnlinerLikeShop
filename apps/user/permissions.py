from rest_framework.permissions import BasePermission

from .models import (
    ACCOUNT_TYPE_MODERATOR,
    ACCOUNT_TYPE_ADMIN,
)


class IsModeratorPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.account_type == ACCOUNT_TYPE_MODERATOR


class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.account_type == ACCOUNT_TYPE_ADMIN
