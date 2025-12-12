from django.contrib.auth.models import AbstractUser


class BaseUser(AbstractUser):
    """Base user model. Admins use this directly (is_superuser=True)."""

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
