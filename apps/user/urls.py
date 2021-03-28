from django.urls import path
from django.urls.conf import include

from .views import (
    ChangePasswordView,
    ObtainExpiringAuthTokenView,
    RegisterView,
    ActivateUserView,
    DeleteUserView,
    ProfileView,
    UserDetailView,
    UserListView,
)
from ..shop.urls import (
    cart_urls,
    order_urls,
)


urlpatterns = [
    path('login/', ObtainExpiringAuthTokenView.as_view()),
    path('register/', RegisterView.as_view()),
    path('activate/<str:token>/', ActivateUserView.as_view()),
    path('current/delete/', DeleteUserView.as_view()),
    path('current/profile/', ProfileView.as_view()),
    path('current/change_password/', ChangePasswordView.as_view()),
    path('current/detail/', UserDetailView.as_view()),
    path('', UserListView.as_view()),

    # shop app
    path('current/cart/', include(cart_urls)),
    path('current/orders/', include(order_urls)),
]
