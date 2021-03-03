from django.urls import path
from .views import ObtainExpiringAuthToken, Register

urlpatterns = [
    path('login/', ObtainExpiringAuthToken.as_view()),
    path('register/', Register.as_view())
]
