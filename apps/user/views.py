from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    ExpiringToken,
    User,
    UserProfile,
)
from .serializers import (
    RegistrationSerializer,
)
from .user_activation import (
    send_activation_email,
    decode_token,
)


class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if not user.is_active:
            # send email
            return Response('User inactive')

        token, created = ExpiringToken.objects.get_or_create(user=user)

        if not created:
            if token.expired():
                token.update()
                token.save()

        return Response({'token': token.key})


class Register(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.error_messages, status=400)

        user = User.objects.create_user(
            serializer.data['email'],
            serializer.data['password'],
            save=False
        )

        try:
            validate_password(serializer.data['password'], user)
        except ValidationError as e:
            return Response({"password_validation_errors": e}, status=400)

        user.save()

        user_profile_data = serializer.data['user_profile'] or {}
        UserProfile(user=user, **(user_profile_data)).save()

        send_activation_email(user)

        return Response('Registered')


class ActivateUser(APIView):
    def get(self, request, token, *args, **kwargs):
        user_id, valid = decode_token(token)
        if not valid:
            return Response('Invalid token')
        else:
            try:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
            except User.DoesNotExist:
                return Response('Invalid token')

            return Response('Activated')
