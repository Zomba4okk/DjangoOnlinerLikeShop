from django.contrib.auth.password_validation import (
    validate_password,
)
from django.core.exceptions import (
    ValidationError,
)

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

    def validate(self, attrs):
        user = User(attrs['email'], attrs['password'])
        try:
            validate_password(attrs['password'], user)
        except ValidationError:
            raise serializers.ValidationError

        return super().validate(attrs)

    def save(self):
        return User.objects.create(
            email=self.validated_data['email'],
            password=self.validated_data['password'],
            user_profile=self.validated_data.get('user_profile', {})
        )


class ChangePasswordSerializer(serializers.Serializer):
    password_max_length = User._meta.get_field('password').max_length
    old_password = serializers.CharField(max_length=password_max_length)
    new_password = serializers.CharField(max_length=password_max_length)


class FullUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'registration_date', 'user_profile')

    user_profile = UserProfileSerializer()


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta(FullUserDetailSerializer.Meta):
        model = User
        fields = ('id', 'email')
