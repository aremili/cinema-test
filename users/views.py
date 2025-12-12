from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import SpectatorRegistrationSerializer


class SpectatorRegistrationView(generics.CreateAPIView):
    """
    Endpoint for spectator registration
    """

    serializer_class = SpectatorRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register as a spectator",
        description="Create a new spectator account.",
        responses={
            201: {"description": "Registration successful"},
            400: {"description": "Validation error"},
        },
        tags=["registration"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Registration successful.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )
