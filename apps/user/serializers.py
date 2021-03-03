from rest_framework import serializers

from .models import (
    SEX_CHOISES,
)


class RegistrationSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=100)

    phone_number = serializers.CharField(max_length=16, required=False)
    first_name = serializers.CharField(max_length=32, required=False)
    last_name = serializers.CharField(max_length=32, required=False)
    middle_name = serializers.CharField(max_length=32, required=False)
    address = serializers.CharField(max_length=150, required=False)
    birth_date = serializers.DateField(required=False)
    sex = serializers.ChoiceField(choices=SEX_CHOISES, required=False)
    # avatar = models.ImageField(
    #     upload_to='/media/user_avatars/', null=True, blank=True
    # )
