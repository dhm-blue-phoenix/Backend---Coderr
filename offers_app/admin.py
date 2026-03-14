from django.contrib import admin
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    model = OfferDetail
    extra = 1


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    inlines = [OfferDetailInline]


admin.site.register(OfferDetail)