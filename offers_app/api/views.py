# Third-party
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

# Local
from core.paginators import StandardResultsSetPagination

from ..models import Offer, OfferDetail
from .filters import OfferFilter
from .permissions import IsBusinessUser, IsOwnerOrReadOnly
from .serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
    """ViewSet for handling CRUD operations for Offers."""

    queryset = Offer.objects.get_queryset_with_min_price()
    serializer_class = OfferSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]

    def get_serializer_class(self):
        """Returns `OfferListSerializer` for list views, and `OfferSerializer` for other actions."""
        if self.action == "list":
            return OfferListSerializer
        return OfferSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            self.permission_classes = [AllowAny]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsBusinessUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Sets the creator of the offer to the currently authenticated user."""
        serializer.save(creator=self.request.user)


class OfferDetailViewSet(RetrieveAPIView):
    """API view for retrieving a single OfferDetail."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
