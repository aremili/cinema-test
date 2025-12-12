import pytest
from django.urls import reverse
from rest_framework import status

from movies.models import Author, AuthorRating


class TestAuthorList:
    """Tests for listing authors"""

    def test_list_authors(self, api_client, author):
        url = reverse("author-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_authors_with_movies(self, api_client, author_with_movie):
        url = reverse("author-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        author_data = response.data[0]
        assert "movies" in author_data
        assert len(author_data["movies"]) == 1
        assert author_data["movies"][0]["title"] == "Test Movie"

    def test_list_authors_by_source(self, api_client, author, author_tmdb):
        url = reverse("author-list")
        response = api_client.get(url, {"source": "tmdb"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == author_tmdb.pk


class TestAuthorRetrieve:
    """Tests for retrieving author"""

    def test_retrieve_author(self, api_client, author):
        url = reverse("author-detail", kwargs={"pk": author.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["biography"] == "Test biography"
        assert response.data["nationality"] == "French"

    def test_retrieve_nonexistent_author(self, api_client, db):
        url = reverse("author-detail", kwargs={"pk": 99999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAuthorUpdate:
    """Tests for updating author"""

    def test_partial_update_author(self, api_client, author, spectator):
        api_client.force_authenticate(user=spectator)
        url = reverse("author-detail", kwargs={"pk": author.pk})
        response = api_client.patch(
            url,
            {"nationality": "Italian"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["nationality"] == "Italian"
        author.refresh_from_db()
        assert author.nationality == "Italian"

    def test_full_update_author(self, api_client, author, spectator):
        api_client.force_authenticate(user=spectator)
        url = reverse("author-detail", kwargs={"pk": author.pk})
        response = api_client.put(
            url,
            {
                "biography": "Updated bio",
                "website": "https://example.com",
                "nationality": "Spanish",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["biography"] == "Updated bio"
        assert response.data["website"] == "https://example.com"


class TestAuthorDelete:
    """Tests for deleting author"""

    def test_delete_author_without_movies_linked(self, api_client, author, spectator):
        api_client.force_authenticate(user=spectator)
        url = reverse("author-detail", kwargs={"pk": author.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Author.objects.filter(pk=author.pk).exists()

    def test_delete_author_with_movies_linked(self, api_client, author_with_movie, spectator):
        api_client.force_authenticate(user=spectator)
        url = reverse("author-detail", kwargs={"pk": author_with_movie.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete author with linked movies" in str(response.data)
        assert Author.objects.filter(pk=author_with_movie.pk).exists()


class TestAuthorRating:

    def test_create_and_update_author_rating(self, api_client, author, spectator):
        api_client.force_authenticate(user=spectator)
        url = reverse("author-rate", kwargs={"pk": author.pk})

        api_client.post(
            url,
            {"score": 7, "review": "Good director"},
            format="json",
        )

        response = api_client.post(
            url,
            {"score": 10, "review": "a masterpiece maker!"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["score"] == 10
        assert response.data["review"] == "a masterpiece maker!"
        assert AuthorRating.objects.filter(spectator=spectator, author=author).count() == 1
