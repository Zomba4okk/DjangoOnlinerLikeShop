from rest_framework import serializers

from .models import (
    User,
    UserProfile,
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'first_name', 'last_name',
                  'middle_name', 'address', 'birth_date', 'sex')


class RegistrationSerializer(serializers.Serializer):
    user = UserRegistrationSerializer()
    user_profile = UserProfileSerializer()
