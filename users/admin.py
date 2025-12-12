from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import BaseUser


@admin.register(BaseUser)
class BaseUserAdmin(DjangoUserAdmin):
    """Admin for BaseUser model (admins only)."""

    list_display = ["username", "email", "is_superuser", "is_active", "date_joined"]
    list_filter = ["is_superuser", "is_staff", "is_active", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]
