# Third-party
from django_filters import rest_framework as filters

# Local
from offers_app.models import Offer


class OfferFilter(filters.FilterSet):
    """
    FilterSet for the Offer model.

    Allows filtering offers by:
    - `min_price`: Minimum price of the offer details.
    - `max_delivery_time`: Maximum delivery time of the offer details.
    - `creator_id`: ID of the offer creator.
    """

    min_price = filters.NumberFilter(field_name="min_price", lookup_expr="gte")
    max_delivery_time = filters.NumberFilter(
        field_name="details__delivery_time_in_days", lookup_expr="lte"
    )
    creator_id = filters.NumberFilter(field_name="creator__id", lookup_expr="exact")

    class Meta:
        model = Offer
        fields = ["creator", "creator_id", "min_price", "max_delivery_time"]
