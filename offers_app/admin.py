# Third-party
from django.contrib import admin

# Local
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """
    Inline representation of OfferDetail model in the admin interface.
    """

    model = OfferDetail
    extra = 1


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """
    Admin interface for the Offer model.
    """

    inlines = [OfferDetailInline]


admin.site.register(OfferDetail)
