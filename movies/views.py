from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Author, Movie, MovieRating, Spectator
from .serializers import AuthorSerializer, MovieRatingSerializer, MovieSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    """
    API to manage authors.
    """
    http_method_names = ["get", "put", "patch", "delete"]

    queryset = Author.objects.prefetch_related("movies").all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]

    def perform_destroy(self, instance):
        if instance.movies.exists():
            raise ValidationError(
                {"detail": "Cannot delete author with linked movies."}
            )
        instance.delete()


class MovieViewSet(viewsets.ModelViewSet):
    """
    API manage  movies.
    """
    http_method_names = ["get", "put", "patch", "post"]
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Movie.objects.all()
        movie_status = self.request.query_params.get("status")
        if movie_status:
            queryset = queryset.filter(status=movie_status)
        return queryset

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
