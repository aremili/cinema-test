from rest_framework import serializers

from .models import Author, Movie


class AuthorNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for Autho"""

    class Meta:
        model = Author
        fields = ["id", "username", "biography", "nationality"]


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie."""

    authors = AuthorNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ["id", "title", "release_date", "status", "authors"]


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author."""

    movies = MovieSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = [
            "id",
            "biography",
            "website",
            "birthdate",
            "nationality",
            "movies",
        ]
