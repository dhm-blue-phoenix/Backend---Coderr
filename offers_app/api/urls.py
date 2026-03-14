# Third-party
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Local
from .views import OfferDetailViewSet, OfferViewSet

router = DefaultRouter()
router.register(r"offers", OfferViewSet, basename="offers")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "offerdetails/<int:pk>/",
        OfferDetailViewSet.as_view(),
        name="offerdetail-detail",
    ),
]
