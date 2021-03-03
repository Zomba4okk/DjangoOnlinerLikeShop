from rest_framework import serializers

from .models import (
    User,
    UserProfile,
)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'first_name', 'last_name',
                  'middle_name', 'address', 'birth_date',
                  'sex', 'avatar')


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'user_profile')

    user_profile = UserProfileSerializer(allow_null=True, required=False)
