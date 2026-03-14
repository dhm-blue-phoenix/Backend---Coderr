from django.contrib import admin
from django.urls import path, include
from .views import BaseInfoView


api_urlpatterns = [
    path("", include("authentication.urls")),
    path("", include("reviews.api.urls")),
    path("", include("offers.api.urls")),
    path("", include("orders.api.urls")),
    path("", include("profiles.api.urls")),
    path("base-info/", BaseInfoView.as_view(), name="base-info"),
]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
]