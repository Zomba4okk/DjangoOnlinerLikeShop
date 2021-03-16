from django.contrib.auth.forms import (
    UserChangeForm as UserChangeFormBase,
    UserCreationForm as UserCreationFormBase,
)

from .models import (
    User,
)


class UserCreationForm(UserCreationFormBase):
    class Meta:
        model = User
        fields = ('email', 'password',)


class UserChangeForm(UserChangeFormBase):
    class Meta:
        model = User
        fields = ('email',)
