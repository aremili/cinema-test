import pytest
from django.urls import reverse
from rest_framework import status

from movies.models import Movie


class TestMovieList:
    """Tests for list of movies"""

    def test_list_movies(self, api_client, movie):
        url = reverse("movie-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_movies_with_authors(self, api_client, movie_with_author):
        url = reverse("movie-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        movie_data = response.data[0]
        assert "authors" in movie_data
        assert len(movie_data["authors"]) == 1

    def test_list_movies_by_status(self, api_client, movie, movie_with_author):
        url = reverse("movie-list")
        response = api_client.get(url, {"status": "released"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["status"] == "released"

    def test_list_movies_filter_by_status_no_match(self, api_client, movie):
        url = reverse("movie-list")
        response = api_client.get(url, {"status": "canceled"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


class TestMovieRetrieve:
    """Tests for retrieving movie"""

    def test_retrieve_movie(self, api_client, movie):
        url = reverse("movie-detail", kwargs={"pk": movie.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Movie"
        assert response.data["status"] == "released"

    def test_retrieve_nonexistent_movie(self, api_client, db):
        url = reverse("movie-detail", kwargs={"pk": 99999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestMovieUpdate:

    def test_partial_update_movie(self, api_client, movie):
        url = reverse("movie-detail", kwargs={"pk": movie.pk})
        response = api_client.patch(
            url,
            {"title": "Updated Title"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"
        movie.refresh_from_db()
        assert movie.title == "Updated Title"

    def test_full_update_movie(self, api_client, movie):
        url = reverse("movie-detail", kwargs={"pk": movie.pk})
        response = api_client.put(
            url,
            {
                "title": "New Title",
                "status": "post_production",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "New Title"
        assert response.data["status"] == "post_production"
