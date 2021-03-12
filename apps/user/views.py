from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    ExpiringAuthToken,
    User,
    UserProfile,
)
from .serializers import (
    ChangePasswordSerializer,
    RegistrationSerializer,
    UserDetailSerializer,
    UserProfileSerializer,
)
from .utils import (
    ActivationEmail,
    ActivationToken,
)


class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if not user.is_active:
            ActivationEmail.send_activation_email(user)
            return Response('User inactive')

        token, created = ExpiringAuthToken.objects.get_or_create(user=user)

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

        ActivationEmail.send_activation_email(user)

        return Response('Registered')


class ActivateUser(APIView):
    def get(self, request, token, *args, **kwargs):
        user_id, valid = ActivationToken.decode_token(token)
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


class DeleteUser(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.is_deleted = True
        user.save()

        return Response({'Deleted'})


class Profile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(
            UserProfileSerializer(
                UserProfile.objects.get(user=request.user)
            ).data
        )

    def post(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(
            UserProfile.objects.get(user=request.user), data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'Profile updated'})


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user: User = request.user

        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'Invalid'})

        if not user.check_password(serializer.data['old_password']):
            return Response({'Incorrect old password'}, status=400)

        try:
            validate_password(serializer.data['new_password'], user)
        except ValidationError as e:
            return Response({"password_validation_errors": e}, status=400)

        user.set_password(serializer.data['new_password'])
        user.save()

        return Response({'Changed'})


class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserDetailSerializer(request.user).data)
