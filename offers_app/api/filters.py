from django_filters import rest_framework as filters

from offers_app.models import Offer


class OfferFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="min_price", lookup_expr="gte")
    max_delivery_time = filters.NumberFilter(
        field_name="details__delivery_time_in_days", lookup_expr="lte"
    )
    creator_id = filters.NumberFilter(field_name="creator__id", lookup_expr="exact")

    class Meta:
        model = Offer
        fields = ["creator", "creator_id", "min_price", "max_delivery_time"]
