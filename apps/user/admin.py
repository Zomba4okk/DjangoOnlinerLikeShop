from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (
    User,
    UserProfile,
)


class UserProfileInline(admin.TabularInline):
    model = UserProfile


class UserModelAdmin(admin.ModelAdmin):
    list_display = ('email', 'registration_date', 'account_type')

    fields_add = ('email', 'password', 'account_type', 'is_active',
                  'is_deleted')
    fields_edit = ('email', 'account_type', 'is_active',
                   'is_deleted', 'registration_date', 'last_login',)

    readonly_fields_add = ('registration_date', 'last_login')
    readonly_fields_edit = readonly_fields_add + ('email',)

    inlines = [UserProfileInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields_edit
        return self.readonly_fields_add

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields_edit
        return self.fields_add

    def save_model(self, request, obj: User, form, change) -> None:
        if form.cleaned_data.get('password'):
            obj.set_password(form.cleaned_data['password'])
        obj.save()


admin.site.register(User, UserModelAdmin)
admin.site.unregister(Group)
