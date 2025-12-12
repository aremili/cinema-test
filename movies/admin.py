from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin

from .models import Author, AuthorRating, Movie, MovieRating, Spectator


class MovieRatingInline(admin.TabularInline):
    """Inline for movie ratings."""

    model = MovieRating
    extra = 0
    readonly_fields = ["created_at", "updated_at"]


class AuthorRatingInline(admin.TabularInline):
    """Inline for author ratings."""

    model = AuthorRating
    extra = 0
    readonly_fields = ["created_at", "updated_at"]


class AuthorMoviesInline(admin.TabularInline):
    """Inline to display movies linked to an author"""

    model = Movie.authors.through
    extra = 0
    verbose_name = "Movie"
    verbose_name_plural = "Movies"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("movie")


class MovieAuthorsInline(admin.TabularInline):
    """Inline to display authors linked to a movi"""

    model = Movie.authors.through
    extra = 0
    verbose_name = "Author"
    verbose_name_plural = "Authors"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author")


class HasMoviesFilter(SimpleListFilter):
    """Filter authors with at least one movie"""

    title = "has movies"
    parameter_name = "has_movies"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Has movies"),
            ("no", "No movies"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(movies__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(movies__isnull=True)
        return queryset


@admin.register(Author)
class AuthorAdmin(UserAdmin):
    """Admin for Author model"""

    list_display = ["username", "get_full_name", "email", "nationality", "birthdate", "movie_count"]
    list_filter = [HasMoviesFilter]
    search_fields = ["username", "first_name", "last_name", "email", "biography"]
    inlines = [AuthorMoviesInline, AuthorRatingInline]

    fieldsets = UserAdmin.fieldsets + (
        ("Author Profile", {"fields": ["biography", "website", "birthdate", "nationality"]}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Author Profile", {"fields": ["biography", "website", "birthdate", "nationality"]}),
    )

    @admin.display(description="Movies")
    def movie_count(self, obj):
        return obj.movies.count()


@admin.register(Spectator)
class SpectatorAdmin(UserAdmin):
    """Admin for Spectator model"""

    list_display = ["username", "email", "date_of_birth", "has_avatar"]
    list_filter = ["date_of_birth", "is_active"]
    search_fields = ["username", "email", "bio"]
    inlines = [MovieRatingInline, AuthorRatingInline]

    fieldsets = UserAdmin.fieldsets + (
        ("Spectator Profile", {"fields": ["bio", "avatar", "date_of_birth"]}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Spectator Profile", {"fields": ["bio", "avatar", "date_of_birth"]}),
    )

    @admin.display(boolean=True, description="Avatar")
    def has_avatar(self, obj):
        return bool(obj.avatar)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Admin for Movie model."""

    list_display = ["title", "release_date", "status", "evaluation", "vote_average", "popularity", "get_authors"]
    list_filter = ["status", "evaluation"]
    search_fields = ["title", "overview", "tagline"]
    filter_horizontal = ["authors"]
    date_hierarchy = "release_date"
    inlines = [MovieAuthorsInline, MovieRatingInline]

    fieldsets = [
        ("Basic Info", {"fields": ["title", "tagline", "overview"]}),
        ("Release", {"fields": ["release_date", "status", "evaluation"]}),
        ("Financials", {"fields": ["budget", "revenue"]}),
        ("Metadata", {"fields": ["original_language", "adult"]}),
        ("Stats", {"fields": ["popularity", "vote_average", "vote_count"]}),
    ]

    readonly_fields = ["created_at", "updated_at"]

    @admin.display(description="Authors")
    def get_authors(self, obj):
        """overview of authors linked to the movie"""
        return ", ".join([str(author) for author in obj.authors.all()[:3]])
