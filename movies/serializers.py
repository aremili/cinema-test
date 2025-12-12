from rest_framework import serializers

from .models import Author, AuthorRating, Movie, MovieRating


class AuthorNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for Author"""

    class Meta:
        model = Author
        fields = ["id", "username", "biography", "nationality"]


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for a Movie."""

    authors = AuthorNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ["id", "title", "release_date", "status", "authors"]


class AuthorRatingSerializer(serializers.ModelSerializer):
    """Rating authors serializer"""

    class Meta:
        model = AuthorRating
        fields = ["id", "score", "review", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author."""

    movies = MovieSerializer(many=True, read_only=True)
    ratings = AuthorRatingSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = [
            "id",
            "first_name",
            "last_name",
            "biography",
            "birthdate",
            "nationality",
            "movies",
            "ratings",
        ]


class MovieRatingSerializer(serializers.ModelSerializer):
    """Serializer for rating movies."""

    class Meta:
        model = MovieRating
        fields = ["id", "score", "review", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MovieNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for movies in favorites"""

    class Meta:
        model = Movie
        fields = ["id", "title", "release_date", "status"]
