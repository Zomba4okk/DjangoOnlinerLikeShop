from django.urls import path
from .views import GetNewAuthToken

urlpatterns = [
    path('login/', GetNewAuthToken.as_view())
]
