# Third-party
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Local
from .views import ProfileViewSet

router = DefaultRouter()
router.register(r"profile", ProfileViewSet, basename="profile")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "profiles/business/",
        ProfileViewSet.as_view({"get": "business"}),
        name="business-profiles",
    ),
    path(
        "profiles/customer/",
        ProfileViewSet.as_view({"get": "customer"}),
        name="customer-profiles",
    ),
]
