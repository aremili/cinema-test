from django.urls import reverse
from rest_framework import status

from movies.models import MovieRating


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

    def test_list_movies_by_source(self, api_client, movie, movie_tmdb):
        url = reverse("movie-list")
        response = api_client.get(url, {"source": "tmdb"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "TMDB Movie"


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
    def test_partial_update_movie(self, api_client, movie, spectator):
        api_client.force_authenticate(user=spectator)
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

    def test_full_update_movie(self, api_client, movie, spectator):
        api_client.force_authenticate(user=spectator)
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


class TestMovieRating:
    def test_create_movie_rating(self, api_client, movie, spectator):
        api_client.force_authenticate(user=spectator)
        url = reverse("movie-rate", kwargs={"pk": movie.pk})
        response = api_client.post(
            url,
            {"score": 8, "review": "Great movie!"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["score"] == 8
        assert response.data["review"] == "Great movie!"
        assert MovieRating.objects.filter(spectator=spectator, movie=movie).exists()

    def test_update_movie_rating(self, api_client, movie, spectator):
        api_client.force_authenticate(user=spectator)
        url = reverse("movie-rate", kwargs={"pk": movie.pk})

        api_client.post(
            url,
            {"score": 7, "review": "Good movie"},
            format="json",
        )

        response = api_client.post(
            url,
            {"score": 9, "review": "Even better when rewatch!"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["score"] == 9
        assert response.data["review"] == "Even better when rewatch!"
        assert MovieRating.objects.filter(spectator=spectator, movie=movie).count() == 1


class TestMovieFavorite:
    """Tests favorite movies"""

    def test_add_movie_to_favorites(self, api_client, movie, spectator):
        api_client.force_authenticate(user=spectator)
        url = reverse("movie-favorite", kwargs={"pk": movie.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert spectator.favorite_movies.filter(pk=movie.pk).exists()

    def test_remove_movie_from_favorites(self, api_client, movie, spectator):
        api_client.force_authenticate(user=spectator)
        spectator.favorite_movies.add(movie)

        url = reverse("movie-favorite", kwargs={"pk": movie.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not spectator.favorite_movies.filter(pk=movie.pk).exists()

    def test_list_my_favorites(self, api_client, movie, spectator):
        api_client.force_authenticate(user=spectator)
        spectator.favorite_movies.add(movie)

        url = reverse("movie-my-favorites")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == movie.pk
