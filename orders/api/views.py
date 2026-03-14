from django.contrib.auth import get_user_model
from rest_framework import viewsets, views, response, status, permissions
from ..models import Order
from offers.models import OfferDetail
from .serializers import OrderSerializer
from .permissions import IsCustomer, IsBusinessUser, IsAdmin


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action == 'destroy':
            self.permission_classes = [IsAdmin]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsBusinessUser]
        elif self.action == 'create':
            self.permission_classes = [IsCustomer]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        if user.type == 'customer':
            return self.queryset.filter(customer=user)
        elif user.type == 'business':
            return self.queryset.filter(business_user=user)
        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return response.Response(
                {"error": "offer_detail_id ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            offer_detail_id = int(offer_detail_id)
            OfferDetail.objects.get(id=offer_detail_id)
        except (ValueError, TypeError):
            return response.Response(
                {"error": "Ungültige Angebotsdetail-ID."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except OfferDetail.DoesNotExist:
            return response.Response(
                {"error": "Ein Angebot mit dieser ID existiert nicht."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.business_user != request.user:
            return response.Response(
                {"error": "Sie haben keine Berechtigung, diese Bestellung zu aktualisieren."},
                status=status.HTTP_403_FORBIDDEN
            )
        new_status = request.data.get('status')
        if not new_status:
             return response.Response(
                {"error": "Das Status-Feld ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(order, data={'status': new_status}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return response.Response(serializer.data)


User = get_user_model()


class OrderCountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(id=business_user_id, type='business')
        except User.DoesNotExist:
            return response.Response({"error": "Business-Benutzer nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return response.Response({'order_count': count})


class CompletedOrderCountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(id=business_user_id, type='business')
        except User.DoesNotExist:
            return response.Response({"error": "Business-Benutzer nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND)
        count = Order.objects.filter(business_user=business_user, status='completed').count()
        return response.Response({'completed_order_count': count})