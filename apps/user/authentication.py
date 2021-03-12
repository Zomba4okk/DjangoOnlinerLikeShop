from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

from .models import ExpiringAuthToken


class ExpiringTokenAuthentication(TokenAuthentication):
    model = ExpiringAuthToken

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if (not token.user.is_active) or token.user.is_deleted:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        if token.expired():
            raise exceptions.AuthenticationFailed('Expired token.')

        return (token.user, token)
