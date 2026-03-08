from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Review(models.Model):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.reviewer.type != 'customer':
            raise ValidationError("Only customers can write reviews.")
        if self.business_user.type != 'business':
            raise ValidationError("Reviews can only be given to businesses.")
        if self.reviewer == self.business_user:
            raise ValidationError("Users cannot review themselves.")

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.business_user.username}"