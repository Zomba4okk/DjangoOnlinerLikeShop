from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models


ACCOUNT_TYPE_STANDART = 'standart'
ACCOUNT_TYPE_MODERATOR = 'moderator'
ACCOUNT_TYPE_ADMIN = 'admin'
ACCOUNT_TYPE_CHOISES = [
    (ACCOUNT_TYPE_STANDART, 'Standart user'),
    (ACCOUNT_TYPE_MODERATOR, 'Moderator'),
    (ACCOUNT_TYPE_ADMIN, 'Admin'),
]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, **kwargs):
        kwargs.setdefault('account_type', ACCOUNT_TYPE_STANDART)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs['account_type'] = ACCOUNT_TYPE_ADMIN
        kwargs['is_active'] = True
        return self._create_user(email, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    is_superuser = False

    email = models.EmailField('email address', unique=True)
    is_active = models.BooleanField('is active', default=False)
    is_deleted = models.BooleanField('is deleted', default=False)
    account_type = models.CharField(choices=ACCOUNT_TYPE_CHOISES,
                                    max_length=32)
    registration_date = models.DateTimeField('registration date',
                                             auto_now_add=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = EMAIL_FIELD
    REQUIRED_FIELDS = []
