import pytest
from django.urls import reverse
from rest_framework import status

from movies.models import Author


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

    def test_partial_update_author(self, api_client, author):
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

    def test_full_update_author(self, api_client, author):
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

    def test_delete_author_without_movies_linked(self, api_client, author):
        url = reverse("author-detail", kwargs={"pk": author.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Author.objects.filter(pk=author.pk).exists()

    def test_delete_author_with_movies_linked(self, api_client, author_with_movie):
        url = reverse("author-detail", kwargs={"pk": author_with_movie.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete author with linked movies" in str(response.data)
        assert Author.objects.filter(pk=author_with_movie.pk).exists()
