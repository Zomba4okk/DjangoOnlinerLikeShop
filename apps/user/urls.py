from django.urls import path
from .views import ObtainExpiringAuthToken

urlpatterns = [
    path('login/', ObtainExpiringAuthToken.as_view())
]
