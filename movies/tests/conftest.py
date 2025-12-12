import pytest
from rest_framework.test import APIClient

from movies.models import Author, Movie, Spectator


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_client_jwt(api_client, spectator):
    """API client with JWT token."""
    response = api_client.post(
        "/api/auth/token/",
        {"username": spectator.username, "password": "testpass123"},
        format="json",
    )
    token = response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def author(db):
    """Test author without movies."""
    return Author.objects.create_user(
        username="test_author",
        email="author@test.com",
        password="testpass123",
        biography="Test biography",
        nationality="French",
    )


@pytest.fixture
def author_with_movie(db):
    """Test author with a linked movie."""
    author = Author.objects.create_user(
        username="author_with_movie",
        email="author2@test.com",
        password="testpass123",
        biography="Another biography",
    )
    movie = Movie.objects.create(
        title="Test Movie",
        overview="A test movie",
    )
    movie.authors.add(author)
    return author


@pytest.fixture
def movie(db):
    """Test movie without authors."""
    return Movie.objects.create(
        title="Test Movie",
        overview="A test movie overview",
        status="released",
    )


@pytest.fixture
def movie_with_author(db, author):
    """Test movie with a linked author."""
    movie = Movie.objects.create(
        title="Movie With Author",
        overview="A movie with an author",
        status="in_production",
    )
    movie.authors.add(author)
    return movie


@pytest.fixture
def spectator(db):
    """Test spectator for rating movies."""
    return Spectator.objects.create_user(
        username="test_spectator",
        email="spectator@test.com",
        password="testpass123",
    )


@pytest.fixture
def movie_tmdb(db):
    """Movie from TMDB"""
    return Movie.objects.create(
        title="TMDB Movie",
        overview="A movie from TMDB",
        status="released",
        source="tmdb",
        tmdb_id=12345,
    )


@pytest.fixture
def author_tmdb(db):
    """Author from TMDB"""
    return Author.objects.create_user(
        username="tmdb_author",
        email="tmdb@test.com",
        password="testpass123",
        source="tmdb",
        tmdb_id=67890,
    )
