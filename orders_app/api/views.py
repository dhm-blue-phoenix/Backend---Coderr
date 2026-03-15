# Third-party
from django.contrib.auth import get_user_model
from rest_framework import permissions, status, views, viewsets
from rest_framework.response import Response

# Local
from offers_app.models import OfferDetail

from ..models import Order
from .permissions import IsAdmin, IsBusinessUser, IsCustomer
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations for Orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action == "destroy":
            self.permission_classes = [IsAdmin]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [IsBusinessUser]
        elif self.action == "create":
            self.permission_classes = [IsCustomer]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        if user.type == "customer":
            return self.queryset.filter(customer=user)
        elif user.type == "business":
            return self.queryset.filter(business_user=user)
        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        offer_detail_id = request.data.get("offer_detail_id")
        if not offer_detail_id:
            return Response(
                {"error": "offer_detail_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            offer_detail_id = int(offer_detail_id)
            OfferDetail.objects.get(id=offer_detail_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid offer detail ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except OfferDetail.DoesNotExist:
            return Response(
                {"error": "An offer with this ID does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.business_user != request.user:
            return Response(
                {
                    "error": "You do not have permission to update this order."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"error": "The status field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(
            order, data={"status": new_status}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


User = get_user_model()


class OrderCountView(views.APIView):
    """
    API view to get the count of in-progress orders for a business user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(id=business_user_id, type="business")
        except User.DoesNotExist:
            return Response(
                {"error": "Business user not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        count = Order.objects.filter(
            business_user=business_user, status="in_progress"
        ).count()
        return Response({"order_count": count})


class CompletedOrderCountView(views.APIView):
    """
    API view to get the count of completed orders for a business user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(id=business_user_id, type="business")
        except User.DoesNotExist:
            return Response(
                {"error": "Business user not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        count = Order.objects.filter(
            business_user=business_user, status="completed"
        ).count()
        return Response({"completed_order_count": count})
