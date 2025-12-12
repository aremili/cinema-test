from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Author
from .serializers import AuthorSerializer


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for viewing authors.
    """

    queryset = Author.objects.prefetch_related("movies").all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
