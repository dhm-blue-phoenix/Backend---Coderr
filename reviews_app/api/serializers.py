from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from auth_app.models import User
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(type="business")
    )
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        reviewer = self.context["request"].user
        business_user = validated_data.get("business_user")

        if Review.objects.filter(
            reviewer=reviewer, business_user=business_user
        ).exists():
            raise serializers.ValidationError(
                "You have already submitted a review for this user."
            )

        validated_data["reviewer"] = reviewer
        return super().create(validated_data)
