from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet, MovieViewSet

router = DefaultRouter()
router.register(r"authors", AuthorViewSet, basename="author")
router.register(r"movies", MovieViewSet, basename="movie")

urlpatterns = [
    path("", include(router.urls)),
]
