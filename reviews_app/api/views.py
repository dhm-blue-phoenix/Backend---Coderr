# Third-party
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

# Local
from ..models import Review
from .permissions import IsReviewerOrReadOnly
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing review instances.
    """

    queryset = Review.objects.all().order_by("-created_at")
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrReadOnly]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["business_user_id", "reviewer_id"]
    ordering_fields = ["rating", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get("business_user_id")
        reviewer_id = self.request.query_params.get("reviewer_id")
        if business_user_id:
            queryset = queryset.filter(business_user__id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer__id=reviewer_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
