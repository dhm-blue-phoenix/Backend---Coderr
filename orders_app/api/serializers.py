# Third-party
from rest_framework import serializers

# Local
from offers_app.models import OfferDetail

from ..models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.

    Handles the creation of orders and validation of the offer detail.
    """
    offer_detail_id = serializers.IntegerField(write_only=True, required=True)
    customer_user = serializers.PrimaryKeyRelatedField(
        source="customer", read_only=True
    )
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)

    title = serializers.CharField(source="offer_detail.title", read_only=True)
    price = serializers.DecimalField(
        source="offer_detail.price", read_only=True, max_digits=10, decimal_places=2
    )
    revisions = serializers.IntegerField(
        source="offer_detail.revisions", read_only=True
    )
    delivery_time_in_days = serializers.IntegerField(
        source="offer_detail.delivery_time_in_days", read_only=True
    )
    features = serializers.JSONField(source="offer_detail.features", read_only=True)
    offer_type = serializers.CharField(source="offer_detail.offer_type", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "title",
            "price",
            "revisions",
            "delivery_time_in_days",
            "features",
            "offer_type",
            "offer_detail_id",
            "customer_user",
            "business_user",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "title",
            "price",
            "revisions",
            "delivery_time_in_days",
            "features",
            "offer_type",
            "customer_user",
            "business_user",
            "created_at",
            "updated_at",
        ]

    def validate_offer_detail_id(self, value):
        """Validates the existence of the offer detail and stores it in the context."""
        try:
            offer_detail = OfferDetail.objects.get(id=value)
            self.context["offer_detail"] = offer_detail
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError(
                "An offer with this ID does not exist."
            )
        except (TypeError, ValueError):
            raise serializers.ValidationError("Invalid offer detail ID.")
        return value

    def create(self, validated_data):
        """Creates an order, assigning the customer, business user, and offer detail."""
        offer_detail = self.context["offer_detail"]
        customer = self.context["request"].user
        if customer.type == "business":
            raise serializers.ValidationError(
                "Business users cannot place orders."
            )
        business_user = offer_detail.offer.creator
        validated_data.pop("offer_detail_id")
        order = Order.objects.create(
            customer=customer,
            business_user=business_user,
            offer_detail=offer_detail,
            status="in_progress",
            **validated_data
        )
        return order
