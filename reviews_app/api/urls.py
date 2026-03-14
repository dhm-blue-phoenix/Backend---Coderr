# Third-party
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Local
from .views import ReviewViewSet

router = DefaultRouter()
router.register(r"reviews", ReviewViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
