# Third-party
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with a `type` field for role-based access."""

    USER_TYPE_CHOICES = (
        ("business", "Business"),
        ("customer", "Customer"),
    )

    email = models.EmailField(unique=True)

    type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default="customer"
    )

    def __str__(self):
        return self.username
