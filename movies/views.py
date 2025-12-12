from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from .models import Author
from .serializers import AuthorSerializer


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
