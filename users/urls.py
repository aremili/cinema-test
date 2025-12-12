from django.urls import path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import SpectatorRegistrationView

urlpatterns = [
    path("register/", SpectatorRegistrationView.as_view(), name="spectator-register"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
]
