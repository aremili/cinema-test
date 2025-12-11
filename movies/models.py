from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    """Base user model for authentication."""

    class UserType(models.TextChoices):
        AUTHOR = "author", "Author"
        SPECTATOR = "spectator", "Spectator"

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.SPECTATOR,
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Author(models.Model):
    """Movie authors"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="author_profile",
    )
    biography = models.TextField(blank=True, default="")
    website = models.URLField(blank=True, default="")
    birthdate = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Spectator(models.Model):
    """Movie spectators"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="spectator_profile",
    )
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Spectator"
        verbose_name_plural = "Spectators"

    def __str__(self):
        return self.user.username


class Movie(models.Model):
    """Movie model"""

    class Status(models.TextChoices):
        RUMORED = "rumored", "Rumored"
        PLANNED = "planned", "Planned"
        IN_PRODUCTION = "in_production", "In Production"
        POST_PRODUCTION = "post_production", "Post Production"
        RELEASED = "released", "Released"
        CANCELED = "canceled", "Canceled"

    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True, default="")
    tagline = models.CharField(max_length=500, blank=True, default="")
    release_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RELEASED,
    )
    budget = models.PositiveBigIntegerField(blank=True, null=True)
    revenue = models.PositiveBigIntegerField(blank=True, null=True)
    original_language = models.CharField(max_length=10, blank=True, default="en")
    adult = models.BooleanField(default=False)
    popularity = models.FloatField(blank=True, null=True)
    vote_average = models.FloatField(blank=True, null=True)
    vote_count = models.PositiveIntegerField(blank=True, null=True)

    authors = models.ManyToManyField(Author, related_name="movies", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"
        ordering = ["-release_date"]

    def __str__(self):
        return self.title


class MovieRating(models.Model):
    """Rating movies by spectators"""

    spectator = models.ForeignKey(
        Spectator,
        on_delete=models.CASCADE,
        related_name="movie_ratings",
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rating from 1 to 10",
    )
    review = models.TextField(blank=True, default="")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Movie Rating"
        verbose_name_plural = "Movie Ratings"
        unique_together = ["spectator", "movie"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.spectator} rated {self.movie}: {self.score}/10"


class AuthorRating(models.Model):
    """Rating authors by spectators"""

    spectator = models.ForeignKey(
        Spectator,
        on_delete=models.CASCADE,
        related_name="author_ratings",
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rating from 1 to 10",
    )
    review = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Author Rating"
        verbose_name_plural = "Author Ratings"
        unique_together = ["spectator", "author"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.spectator} rated {self.author}: {self.score}/10"
