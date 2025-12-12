from django.contrib import admin
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


@admin.register(Author)
class AuthorAdmin(UserAdmin):
    """Admin for Author model - extends UserAdmin."""

    list_display = ["username", "get_full_name", "email", "nationality", "birthdate"]
    list_filter = ["nationality", "is_active"]
    search_fields = ["username", "first_name", "last_name", "email", "biography"]
    inlines = [AuthorRatingInline]

    fieldsets = UserAdmin.fieldsets + (
        ("Author Profile", {"fields": ["biography", "website", "birthdate", "nationality"]}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Author Profile", {"fields": ["biography", "website", "birthdate", "nationality"]}),
    )


@admin.register(Spectator)
class SpectatorAdmin(UserAdmin):
    """Admin for Spectator model - extends UserAdmin."""

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

    list_display = ["title", "release_date", "status", "evaluation", "vote_average", "popularity"]
    list_filter = ["status", "evaluation", "adult", "original_language"]
    search_fields = ["title", "overview", "tagline"]
    filter_horizontal = ["authors"]
    date_hierarchy = "release_date"
    inlines = [MovieRatingInline]

    fieldsets = [
        ("Basic Info", {"fields": ["title", "tagline", "overview"]}),
        ("Release", {"fields": ["release_date", "status", "evaluation"]}),
        ("Financials", {"fields": ["budget", "revenue"], "classes": ["collapse"]}),
        ("Metadata", {"fields": ["original_language", "adult"]}),
        ("Stats", {"fields": ["popularity", "vote_average", "vote_count"]}),
        ("Relationships", {"fields": ["authors"]}),
    ]

    readonly_fields = ["created_at", "updated_at"]
