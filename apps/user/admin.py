from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

import nested_admin

from .forms import (
    UserChangeForm,
    UserCreationForm,
)
from .models import (
    User,
    UserProfile,
)
from apps.shop.models import (
    Cart,
    CartProductM2M,
)


class UserProfileInline(nested_admin.NestedStackedInline):
    model = UserProfile


class CartProductM2MInline(nested_admin.NestedStackedInline):
    model = CartProductM2M
    extra = 1


class CartInline(nested_admin.NestedStackedInline):
    model = Cart
    inlines = [CartProductM2MInline]


class UserAdmin(nested_admin.NestedModelAdmin, BaseUserAdmin):
    model = User

    inlines = [UserProfileInline, CartInline]

    add_form = UserCreationForm
    form = UserChangeForm

    readonly_fields = ('registration_date', 'last_login')
    fieldsets = (
        (None, {'fields': ('email',)}),
        (None, {'fields': ('account_type',)}),
        (None, {'fields': ('registration_date', 'last_login')}),
        (None, {'fields': ('is_active', 'is_deleted')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'account_type',
                       'is_active', 'is_deleted')
        }
        ),
    )

    list_display = ('email', 'account_type', 'registration_date', 'last_login',
                    'is_active', 'is_deleted')
    list_filter = ('account_type', 'is_active', 'is_deleted')
    search_fields = ('email',)
    ordering = ('-id',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
