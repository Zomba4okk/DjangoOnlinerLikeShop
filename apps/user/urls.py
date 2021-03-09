from django.urls import path
from .views import (
    ChangePassword,
    ObtainExpiringAuthToken,
    Register,
    ActivateUser,
    DeleteUser,
    Profile,
)


urlpatterns = [
    path('login/', ObtainExpiringAuthToken.as_view()),
    path('register/', Register.as_view()),
    path('activate/<str:token>/', ActivateUser.as_view()),
    path('delete/<str:email>/', DeleteUser.as_view()),
    path('profile/', Profile.as_view()),
    path('change_password/', ChangePassword.as_view()),
]
