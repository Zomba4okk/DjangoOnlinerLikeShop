from django.contrib.auth.forms import (
    UserChangeForm as UserChangeFormBase,
    UserCreationForm as UserCreationFormBase,
)

from .models import (
    User,
    UserProfile,
)
from apps.shop.models import (
    Cart,
)


class UserCreationForm(UserCreationFormBase):
    class Meta:
        model = User
        fields = ('email', 'password',)

    def save(self, commit: bool):
        user = super().save()
        if not hasattr(user, 'user_profile'):
            UserProfile.objects.create(user=user)
        if not hasattr(user, 'cart'):
            Cart.objects.create(user=user)

        return user


class UserChangeForm(UserChangeFormBase):
    class Meta:
        model = User
        fields = ('email',)
