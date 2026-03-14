# Third-party
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Local
from profiles_app.models import Profile

from .permissions import IsOwnerOrReadOnly
from .serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    @action(detail=False)
    def business(self, request):
        business_profiles = self.get_queryset().filter(user__type="business")
        serializer = self.get_serializer(business_profiles, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def customer(self, request):
        customer_profiles = self.get_queryset().filter(user__type="customer")
        serializer = self.get_serializer(customer_profiles, many=True)
        return Response(serializer.data)
