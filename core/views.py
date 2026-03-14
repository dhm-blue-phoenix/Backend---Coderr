from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Avg
from reviews_app.models import Review
from profiles_app.models import Profile
from offers_app.models import Offer
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {"error": "An unexpected error occurred. Please try again later."},
            status=500
        )

    return response


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        
        average_rating = round(average_rating, 1)

        business_profile_count = Profile.objects.filter(user__type='business').count()
        offer_count = Offer.objects.count()

        return Response({
            'review_count': review_count,
            'average_rating': average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count,
        })