import pytest
from django.urls import reverse
from rest_framework import status

from movies.models import Spectator


class TestSpectatorRegistration:
    """Tests for registration"""

    def test_register_spectator(self, api_client, db):
        url = reverse("spectator-register")
        response = api_client.post(
            url,
            {
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "Registration successful."
        assert response.data["user"]["username"] == "newuser"
        assert Spectator.objects.filter(username="newuser").exists()

    def test_register_password_mismatch(self, api_client, db):
        url = reverse("spectator-register")
        response = api_client.post(
            url,
            {
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "SecurePass123!",
                "password_confirm": "DifferentPass!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data

    def test_register_duplicate_username(self, api_client, db):
        Spectator.objects.create_user(
            username="existinguser",
            email="existing@test.com",
            password="TestPass123!",
        )

        url = reverse("spectator-register")
        response = api_client.post(
            url,
            {
                "username": "existinguser",
                "email": "new@test.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data
