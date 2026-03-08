from rest_framework import serializers
from ..models import Offer, OfferDetail
from authentication.api.serializers import UserDetailsSerializer


class OfferDetailSerializer(serializers.ModelSerializer):

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


class OfferDetailInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ["title", "revisions", "delivery_time_in_days", "price", "features", "offer_type"]


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailInputSerializer(many=True, write_only=True)
    user = serializers.ReadOnlyField(source='creator.id')
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
        ret = super().to_representation(instance)
        details = []
        for detail in instance.details.all():
            details.append({
                "id": detail.id,
                "url": f"/api/offerdetails/{detail.id}/"
            })
        ret['details'] = details
        return ret

    def validate_details(self, value):
        if not self.instance and len(value) != 3:
            raise serializers.ValidationError("Genau 3 Angebotsdetails (basic, standard, premium) sind erforderlich.")
        return value

    def create(self, validated_data):
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)
        instance = super().update(instance, validated_data)

        if details_data is not None:
            existing_details = {d.offer_type: d for d in instance.details.all()}
            for detail_data in details_data:
                offer_type = detail_data.get("offer_type")
                detail = existing_details.get(offer_type)
                if detail:
                    for attr, value in detail_data.items():
                        setattr(detail, attr, value)
                    detail.save()
                else:
                    OfferDetail.objects.create(offer=instance, **detail_data)
        return instance


class OfferListSerializer(serializers.ModelSerializer):
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='creator.id')
    user_details = UserDetailsSerializer(source="creator", read_only=True)
    details = serializers.SerializerMethodField()

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
        return obj.min_price

    def get_min_delivery_time(self, obj):
        return obj.min_delivery_time
    
    def get_details(self, obj):
        from rest_framework.reverse import reverse
        details_list = []
        for detail in obj.details.all():
            details_list.append({
                "id": detail.id,
                "url": f"/api/offerdetails/{detail.id}/"
            })
        return details_list