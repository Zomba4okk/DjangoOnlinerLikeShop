from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
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
    EmailUtil,
    ActivationTokenUtil,
)


class ObtainExpiringAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if not user.is_active:
            EmailUtil.send_activation_email(user, raise_exception=False)
            return Response(status=HTTP_400_BAD_REQUEST)

        token, created = ExpiringAuthToken.objects.get_or_create(user=user)

        if not created:
            if token.expired():
                token.update()
                token.save()

        return Response({'token': token.key})


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            serializer.data['email'],
            serializer.data['password'],
            save=False
        )

        try:
            validate_password(serializer.data['password'], user)
        except ValidationError as e:
            return Response({"password_validation_errors": e},
                            status=HTTP_400_BAD_REQUEST)

        user.save()

        user_profile_data = serializer.data['user_profile'] or {}
        UserProfile(user=user, **(user_profile_data)).save()

        EmailUtil.send_activation_email(user, raise_exception=False)

        return Response(status=HTTP_204_NO_CONTENT)


class ActivateUserView(APIView):
    def get(self, request, token, *args, **kwargs):
        user_id, valid = ActivationTokenUtil.decode_token(token)
        if not valid:
            return Response(status=HTTP_400_BAD_REQUEST)
        else:
            try:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
            except User.DoesNotExist:
                return Response(status=HTTP_400_BAD_REQUEST)

            return Response(status=HTTP_204_NO_CONTENT)


class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.is_deleted = True
        user.save()

        return Response(status=HTTP_204_NO_CONTENT)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(
            UserProfileSerializer(
                UserProfile.objects.get(user=request.user)
            ).data
        )

    def patch(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(
            UserProfile.objects.get(user=request.user), data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user: User = request.user

        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        if not user.check_password(serializer.data['old_password']):
            return Response({'error': 'Incorrect old password'},
                            status=HTTP_400_BAD_REQUEST)

        try:
            validate_password(serializer.data['new_password'], user)
        except ValidationError as e:
            return Response({'password_validation_errors': e},
                            status=HTTP_400_BAD_REQUEST)

        user.set_password(serializer.data['new_password'])
        user.save()

        return Response(status=HTTP_204_NO_CONTENT)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserDetailSerializer(request.user).data)
