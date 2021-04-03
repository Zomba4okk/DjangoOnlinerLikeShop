from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
)
from django.db import models
from django.utils import timezone

from rest_framework.authtoken.models import Token

from apps.shop.models import (
    Cart,
)


ACCOUNT_TYPE_STANDARD = 'standard'
ACCOUNT_TYPE_MODERATOR = 'moderator'
ACCOUNT_TYPE_ADMIN = 'admin'
ACCOUNT_TYPE_CHOICES = [
    (ACCOUNT_TYPE_STANDARD, 'Standard user'),
    (ACCOUNT_TYPE_MODERATOR, 'Moderator'),
    (ACCOUNT_TYPE_ADMIN, 'Admin'),
]

SEX_M = 'm'
SEX_F = 'f'
SEX_CHOICES = [
    (SEX_M, 'Male'),
    (SEX_F, 'Female'),
]


class ExpiringAuthToken(Token):
    #                               d    h    m    s
    EXPIRATION_PERIOD_IN_SECONDS = 30 * 24 * 60 * 60

    key = models.CharField("Key", max_length=40, unique=True)

    def expired(self):
        return (timezone.now() - self.created).total_seconds() \
               >= self.EXPIRATION_PERIOD_IN_SECONDS

    def update(self):
        self.key = self.generate_key()
        self.created = timezone.now()


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        email = self.normalize_email(email)
        user_profile_data = kwargs.pop('user_profile', {})

        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, **user_profile_data)

        Cart.objects.create(user=user)

        return user

    def create_user(self, email, password, **kwargs):
        kwargs.setdefault('account_type', ACCOUNT_TYPE_STANDARD)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs['account_type'] = ACCOUNT_TYPE_ADMIN
        kwargs['is_active'] = True
        return self._create_user(email, password, **kwargs)


class User(AbstractBaseUser):
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    objects = UserManager()

    email = models.EmailField('email address', unique=True)
    is_active = models.BooleanField('is active', default=False)
    is_deleted = models.BooleanField('is deleted', default=False)
    account_type = models.CharField(choices=ACCOUNT_TYPE_CHOICES,
                                    max_length=32)
    registration_date = models.DateTimeField('registration date',
                                             auto_now_add=True)

    @property
    def is_staff(self):
        return self.account_type == ACCOUNT_TYPE_ADMIN

    def has_module_perms(self, *args, **kwargs):
        return self.account_type == ACCOUNT_TYPE_ADMIN

    def has_perm(self, *args, **kwargs):
        return self.account_type == ACCOUNT_TYPE_ADMIN

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = EMAIL_FIELD
    REQUIRED_FIELDS = []


class UserProfile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE,
                                related_name='user_profile')

    phone_number = models.CharField(max_length=16, null=True, blank=True)
    first_name = models.CharField(max_length=32, null=True, blank=True)
    last_name = models.CharField(max_length=32, null=True, blank=True)
    middle_name = models.CharField(max_length=32, null=True, blank=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES,
                           null=True, blank=True)
    avatar = models.ImageField(
        upload_to='user_avatars/', null=True, blank=True
    )
