# Third-party
from rest_framework import serializers

# Local
from auth_app.api.serializers import UserDetailsSerializer

from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializes `OfferDetail` instances, converting the `price` field to a float."""
    price = serializers.FloatField()

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferDetailListSerializer(serializers.ModelSerializer):
    """Serializer for the OfferDetail model for list views, including a hyperlink."""
    url = serializers.HyperlinkedIdentityField(
        view_name="offerdetail-detail", lookup_field="pk"
    )
    price = serializers.FloatField()

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "url",
        ]


class OfferDetailInputSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating OfferDetail instances."""
    price = serializers.FloatField()

    class Meta:
        model = OfferDetail
        fields = [
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferSerializer(serializers.ModelSerializer):
    """
    Main serializer for the Offer model, handling nested creation and updates of OfferDetails.
    """
    details = OfferDetailInputSerializer(many=True)
    user = serializers.ReadOnlyField(source="creator.id")
    user_details = UserDetailsSerializer(source="creator", read_only=True)
    min_price = serializers.ReadOnlyField()
    min_delivery_time = serializers.ReadOnlyField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "description",
            "image",
            "user_details",
            "details",
            "min_price",
            "min_delivery_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user_details"]

    def to_representation(self, instance):
        """Dynamically selects the detail serializer based on the view's action."""
        ret = super().to_representation(instance)
        details = []
        request = self.context.get("request")

        # Use serializer with URL for 'retrieve' action, and without for others.
        if (
            self.context.get("view") is not None
            and self.context["view"].action == "retrieve"
        ):
            DetailSerializer = OfferDetailListSerializer
        else:
            DetailSerializer = OfferDetailSerializer

        for detail in instance.details.all():
            details.append(DetailSerializer(detail, context={"request": request}).data)

        ret["details"] = details
        return ret

    def validate_details(self, value):
        """Ensures that exactly three offer details are provided during creation."""
        if not self.instance and len(value) != 3:
            raise serializers.ValidationError(
                "Exactly 3 offer details (basic, standard, premium) are required."
            )
        return value

    def create(self, validated_data):
        """Handles the creation of an `Offer` and its associated `OfferDetail` instances from nested data."""
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        """Handles updates to the `Offer` and its nested `OfferDetail` instances."""
        details_data = validated_data.pop("details", None)
        instance = super().update(instance, validated_data)

        if details_data is not None:
            existing_details = {d.offer_type: d for d in instance.details.all()}
            for detail_data in details_data:
                offer_type = detail_data.get("offer_type")
                if not offer_type:
                    raise serializers.ValidationError("Missing offer_type")
                detail = existing_details.get(offer_type)
                if detail:
                    for attr, value in detail_data.items():
                        setattr(detail, attr, value)
                    detail.save()
                else:
                    OfferDetail.objects.create(offer=instance, **detail_data)
        return instance


class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing offers, including annotated fields for min_price and min_delivery_time.
    """
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source="creator.id")
    user_details = UserDetailsSerializer(source="creator", read_only=True)
    details = OfferDetailListSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "min_price",
            "min_delivery_time",
            "user_details",
            "details",
            "created_at",
            "updated_at",
        ]

    def get_min_price(self, obj):
        """Returns the `min_price` annotated on the queryset."""
        return obj.min_price

    def get_min_delivery_time(self, obj):
        """Returns the `min_delivery_time` annotated on the queryset."""
        return obj.min_delivery_time
