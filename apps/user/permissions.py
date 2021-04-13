from rest_framework.permissions import (
    IsAuthenticated,
)

from .models import (
    ACCOUNT_TYPE_MODERATOR,
    ACCOUNT_TYPE_ADMIN,
)


class IsModeratorPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and \
               request.user.account_type == ACCOUNT_TYPE_MODERATOR


class IsAdminPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and \
               request.user.account_type == ACCOUNT_TYPE_ADMIN
