from rest_framework import serializers

from .models import Author, Movie


class MovieSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Movie
        fields = ["id", "title", "release_date", "status"]


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author with nested movies."""

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
