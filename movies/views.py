from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Author.objects.prefetch_related("movies").all()
        source = self.request.query_params.get("source")
        if source:
            queryset = queryset.filter(source=source)
        return queryset
    
    @extend_schema(
        summary="List all authors",
        description="Returns a list of all authors.",
        parameters=[
            OpenApiParameter(
                name="source",
                description="Filter by source",
                required=False,
                enum=["admin", "tmdb"],
            ),
        ],
        responses={200: AuthorSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Retrieve an author",
        description="Returns a specific author.",
        responses={200: AuthorSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update an author",
        description="Update a specific author.",
        responses={200: AuthorSerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial update an author",
        description="Partial update a specific author.",
        responses={200: AuthorSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if instance.movies.exists():
            raise ValidationError(
                {"detail": "Cannot delete author with linked movies."}
            )
        instance.delete()

    @extend_schema(
        summary="Rate an author/director",
        description="Allow a spectator to rate an author/director from 1-10.",
        request=AuthorRatingSerializer,
        responses={
            201: AuthorRatingSerializer,
            200: AuthorRatingSerializer,
            403: OpenApiResponse(description="Only spectators can rate authors."),
        },
    )
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
    API to manage movies.
    """

    http_method_names = ["get", "put", "patch", "post", "delete"]
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Movie.objects.all()
        movie_status = self.request.query_params.get("status")
        source = self.request.query_params.get("source")
        if movie_status:
            queryset = queryset.filter(status=movie_status)
        if source:
            queryset = queryset.filter(source=source)
        return queryset

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Deleting movies is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Creating movies is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @extend_schema(
        summary="List all movies",
        description="Returns a list of all movies.",
        parameters=[
            OpenApiParameter(
                name="status",
                description="Filter by movie status",
                required=False,
                enum=["rumored", "planned", "in_production", "post_production", "released", "canceled"],
            ),
            OpenApiParameter(
                name="source",
                description="Filter by source",
                required=False,
                enum=["admin", "tmdb"],
            ),
        ],
        responses={200: MovieSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a movie",
        description="Returns a specific movie.",
        responses={200: MovieSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update a movie",
        description="Update a specific movie.",
        responses={200: MovieSerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial update a movie",
        description="Partial update a specific movie.",
        responses={200: MovieSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Rate a movie",
        description="Allow a spectator to rate a movie from 1-10.",
        request=MovieRatingSerializer,
        responses={
            201: MovieRatingSerializer,
            200: MovieRatingSerializer,
            403: OpenApiResponse(description="Only spectators can rate movies."),
        },
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

    @extend_schema(
        summary="Add/remove movie from favorites",
        description="Allow a spectator to add or remove a movie from list of spectator favorites movies.",
        responses={
            204: OpenApiResponse(description="Movie removed from favorites"),
            201: OpenApiResponse(description="Movie added to favorites"),
            404: OpenApiResponse(description="Movie not found"),
            403: OpenApiResponse(description="Only spectators can manage favorites"),
        },
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

    @extend_schema(
        summary="List of spectator favorites movies",
        description="Get list of spectator favorites movies.",
        responses={
            200: MovieSerializer(many=True),
            403: OpenApiResponse(description="Only spectators can get favorites movies."),
        },
    )
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
