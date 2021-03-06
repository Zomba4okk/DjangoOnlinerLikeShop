from django.urls import path
from .views import (
    ObtainExpiringAuthToken,
    Register,
    ActivateUser,
)


urlpatterns = [
    path('login/', ObtainExpiringAuthToken.as_view()),
    path('register/', Register.as_view()),
    path('activate/<str:token>/', ActivateUser.as_view())
]
