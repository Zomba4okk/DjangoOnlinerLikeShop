from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

from .models import ExpiringToken


class ExpiringTokenAuthentication(TokenAuthentication):
    model = ExpiringToken

    def authenticate_credentials(self, key):
        if key.expired():
            raise exceptions.AuthenticationFailed('Expired token.')

        super().authenticate_credentials(key)
