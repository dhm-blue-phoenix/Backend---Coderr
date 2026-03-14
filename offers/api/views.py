from rest_framework import viewsets, filters
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferListSerializer, OfferDetailListSerializer
from .permissions import IsOwnerOrReadOnly, IsBusinessUser
from core.paginators import StandardResultsSetPagination
from .filters import OfferFilter


class OfferViewSet(viewsets.ModelViewSet):
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
        if self.action == "list":
            return OfferListSerializer
        return OfferSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        if self.action == 'create':
            return [IsBusinessUser()]
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class OfferDetailViewSet(RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailListSerializer
    permission_classes = [IsAuthenticated]