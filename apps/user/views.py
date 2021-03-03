from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from .models import (
    ExpiringToken,
    User, UserProfile,
)
from .serializers import (
    RegistrationSerializer,
)


class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, created = ExpiringToken.objects.get_or_create(user=user)

        if not created:
            if token.expired():
                token.delete()
                token = ExpiringToken.objects.create(user=user)

        return Response({'token': token.key})


class Register(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.data

        user = User.objects.create_user(
            serializer_data.pop('email'),
            serializer_data.pop('password')
        )
        UserProfile(user=user, **serializer_data).save()

        return Response()
