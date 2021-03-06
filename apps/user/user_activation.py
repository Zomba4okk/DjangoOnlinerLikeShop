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
from django.core.mail import send_mail
from django.utils import timezone

import environ
from cryptography.fernet import Fernet

env = environ.Env()

FORMAT_REGEX = r'^_*\d+(\.[\d]{1,6})?_\d+$'
TOKEN_STRING_LENGTH = 32
ENCODING = 'utf8'
# key\/ must be 32 bytes
ENCRYPTION_KEY = env('USER_ACTIVATION_ENCRYPTION_KEY')
EXPIRATION_PERIOD_IN_SECONDS = 1800  # 30 mins

coder = Fernet(
    base64.urlsafe_b64encode(
        ENCRYPTION_KEY.encode(ENCODING)
    )
)


def get_raw_token_string(user_id: int) -> str:
    return \
        '{:22.6f}_{}'.format(
            datetime.timestamp(timezone.now()),
            user_id
        ).lstrip().rjust(TOKEN_STRING_LENGTH, '_')


def get_encrypted_token_string(user_id: int) -> str:
    return coder.encrypt(
        get_raw_token_string(user_id).encode(ENCODING)
    ).decode(ENCODING)


def get_decrypted_token_string(encrypted_token: str) -> str:
    return coder.decrypt(
        encrypted_token.encode(ENCODING)
    ).decode(ENCODING)


def validate_token(decrypted_token: str) -> bool:
    if len(decrypted_token) != TOKEN_STRING_LENGTH:
        return False

    return bool(re.match(FORMAT_REGEX, decrypted_token))


def get_datetime_and_user_id(token: str) -> Tuple[datetime, int]:
    split_token = token.lstrip('_').split('_')
    return (
        datetime.fromtimestamp(
            float(split_token[0]), tz=timezone.get_current_timezone()
        ),
        int(split_token[1])
    )


def decode_token(encrypted_token: str) -> Tuple[Union[int, None], bool]:
    token = get_decrypted_token_string(encrypted_token)
    if not validate_token(token):
        return None, False

    dt, user_id = get_datetime_and_user_id(token)

    return (
        user_id,
        (timezone.now() - dt).total_seconds() < EXPIRATION_PERIOD_IN_SECONDS
    )


def send_activation_email(user):
    send_mail(
        'Account activation',
        f'Activation link: {settings.USER_ACTIVATION_URI}'
        f'{get_encrypted_token_string(user.id)}',
        env('EMAIL_ADDRESS'),
        [user.email]
    )
