# Generates user activation token in the format:
# <'_' * n><timestamp>_<user id>,
# with such n so that total len = 32
# e.g.: ____________1614873250.975825_25
# regex: ^_*\d+(\.[\d]{1,6})?_\d+$


import base64
import re
from datetime import datetime
from typing import Tuple, Union

from django.conf import settings
from django.db import models
from django.utils import timezone

from rest_framework.authtoken.models import Token

from cryptography.fernet import Fernet


class ExpiringAuthToken(Token):
    #                               d    h    m    s
    expiration_period_in_seconds = 30 * 24 * 60 * 60

    key = models.CharField("Key", max_length=40, unique=True)

    def expired(self):
        return (timezone.now() - self.created).total_seconds() \
               >= self.expiration_period_in_seconds

    def update(self):
        self.key = self.generate_key()
        self.created = timezone.now()


class ActivationToken:
    FORMAT_REGEX = r'^_*\d+(\.[\d]{1,6})?_\d+$'
    TOKEN_STRING_LENGTH = 32
    ENCODING = 'utf8'

    coder = Fernet(
        base64.urlsafe_b64encode(
            settings.USER_ACTIVATION_ENCRYPTION_KEY.encode(ENCODING)
        )
    )

    @classmethod
    def get_raw_token_string(cls, user_id: int) -> str:
        return \
            '{:22.6f}_{}'.format(
                datetime.timestamp(timezone.now()),
                user_id
            ).lstrip().rjust(cls.TOKEN_STRING_LENGTH, '_')

    @classmethod
    def get_encrypted_token_string(cls, user_id: int) -> str:
        return cls.coder.encrypt(
            cls.get_raw_token_string(user_id).encode(cls.ENCODING)
        ).decode(cls.ENCODING)

    @classmethod
    def get_decrypted_token_string(cls, encrypted_token: str) -> str:
        return cls.coder.decrypt(
            encrypted_token.encode(cls.ENCODING)
        ).decode(cls.ENCODING)

    @classmethod
    def validate_token(cls, decrypted_token: str) -> bool:
        if len(decrypted_token) != cls.TOKEN_STRING_LENGTH:
            return False

        return bool(re.match(cls.FORMAT_REGEX, decrypted_token))

    @classmethod
    def get_datetime_and_user_id(cls, token: str) -> Tuple[datetime, int]:
        split_token = token.lstrip('_').split('_')
        return (
            datetime.fromtimestamp(
                float(split_token[0]), tz=timezone.get_current_timezone()
            ),
            int(split_token[1])
        )

    @classmethod
    def decode_token(cls, encrypted_token: str) -> Tuple[Union[int, None], bool]:  # noqa
        token = cls.get_decrypted_token_string(encrypted_token)
        if not cls.validate_token(token):
            return None, False

        dt, user_id = cls.get_datetime_and_user_id(token)

        return (
            user_id,
            (timezone.now() - dt).total_seconds()
            < settings.USER_ACTIVATION_EXPIRATION_PERIOD_IN_SECONDS
        )
