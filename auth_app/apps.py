# Third-party
from django.apps import AppConfig


class AuthConfig(AppConfig):
    """
    App configuration for the auth_app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_app"
