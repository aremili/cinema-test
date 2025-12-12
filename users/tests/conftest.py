import pytest
from rest_framework.test import APIClient

from movies.models import Spectator


@pytest.fixture
def api_client():
    return APIClient()
