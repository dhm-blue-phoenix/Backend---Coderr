# Third-party
from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """
    AppConfig for the profiles_app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles_app"

    def ready(self):
        # Local
        import profiles_app.signals
