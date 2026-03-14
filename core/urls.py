from django.contrib import admin
from django.urls import path, include
from .views import BaseInfoView


api_urlpatterns = [
    path("", include("auth_app.urls")),
    path("", include("reviews_app.api.urls")),
    path("", include("offers_app.api.urls")),
    path("", include("orders_app.api.urls")),
    path("", include("profiles_app.api.urls")),
    path("base-info/", BaseInfoView.as_view(), name="base-info"),
]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
]