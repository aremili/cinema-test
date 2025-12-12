from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Author, AuthorRating, Movie, MovieRating, Spectator
from .serializers import (
    AuthorRatingSerializer,
    AuthorSerializer,
    MovieNestedSerializer,
    MovieRatingSerializer,
    MovieSerializer,
)


class AuthorViewSet(viewsets.ModelViewSet):
    """
    API to manage authors.
    """
    http_method_names = ["get", "put", "patch", "delete", "post"]

    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Author.objects.prefetch_related("movies").all()
        source = self.request.query_params.get("source")
        if source:
            queryset = queryset.filter(source=source)
        return queryset

    def perform_destroy(self, instance):
        if instance.movies.exists():
            raise ValidationError(
                {"detail": "Cannot delete author with linked movies."}
            )
        instance.delete()

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        serializer_class=AuthorRatingSerializer,
    )
    def rate(self, request, pk=None):
        author = self.get_object()

        try:
            spectator = Spectator.objects.get(pk=request.user.pk)
        except Spectator.DoesNotExist:
            return Response(
                {"detail": "Only spectators can rate authors."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rating, created = AuthorRating.objects.update_or_create(
            spectator=spectator,
            author=author,
            defaults={
                "score": serializer.validated_data["score"],
                "review": serializer.validated_data.get("review", ""),
            },
        )

        response_serializer = AuthorRatingSerializer(rating)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MovieViewSet(viewsets.ModelViewSet):
    """
    API manage  movies.
    """
    http_method_names = ["get", "put", "patch", "post", "delete"]
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Movie.objects.all()
        movie_status = self.request.query_params.get("status")
        source = self.request.query_params.get("source")
        if movie_status:
            queryset = queryset.filter(status=movie_status)
        if source:
            queryset = queryset.filter(source=source)
        return queryset

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Deleting movies is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Creating movies is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        serializer_class=MovieRatingSerializer,
    )
    def rate(self, request, pk=None):
        movie = self.get_object()

        try:
            spectator = Spectator.objects.get(pk=request.user.pk)
        except Spectator.DoesNotExist:
            return Response(
                {"detail": "Only spectators can rate movies."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rating, created = MovieRating.objects.update_or_create(
            spectator=spectator,
            movie=movie,
            defaults={
                "score": serializer.validated_data["score"],
                "review": serializer.validated_data.get("review", ""),
            },
        )

        response_serializer = MovieRatingSerializer(rating)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="favorite",
    )
    def favorite(self, request, pk=None):
        movie = self.get_object()

        try:
            spectator = Spectator.objects.get(pk=request.user.pk)
        except Spectator.DoesNotExist:
            return Response(
                {"detail": "Only spectators can manage favorites."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "POST":
            spectator.favorite_movies.add(movie)
            return Response(
                {"detail": f"'{movie.title}' added to favorites."},
                status=status.HTTP_201_CREATED,
            )
        elif request.method == "DELETE":
            if not spectator.favorite_movies.filter(pk=movie.pk).exists():
                return Response(
                    {"detail": "Movie not in favorites."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            spectator.favorite_movies.remove(movie)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="favorites",
    )
    def my_favorites(self, request):
        try:
            spectator = Spectator.objects.get(pk=request.user.pk)
        except Spectator.DoesNotExist:
            return Response(
                {"detail": "Only spectators have favorites movies."},
                status=status.HTTP_403_FORBIDDEN,
            )

        movies = spectator.favorite_movies.all()
        serializer = MovieNestedSerializer(movies, many=True)
        return Response(serializer.data)
