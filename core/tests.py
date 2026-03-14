from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class BaseInfoTests(APITestCase):
    def setUp(self):
        self.url = "/api/base-info/"

    def test_base_info_no_auth_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_response_fields(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("review_count", response.data)
        self.assertIn("average_rating", response.data)
        self.assertIn("business_profile_count", response.data)
        self.assertIn("offer_count", response.data)

    def test_base_info_review_count_is_int(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.data["review_count"], int)

    def test_base_info_business_profile_count_is_int(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.data["business_profile_count"], int)

    def test_base_info_offer_count_is_int(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.data["offer_count"], int)

    def test_base_info_average_rating_is_numeric(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.data["average_rating"], (float, int))

    def test_base_info_average_rating_one_decimal(self):
        response = self.client.get(self.url)
        avg = response.data["average_rating"]
        self.assertEqual(round(avg, 1), avg)

    def test_base_info_server_error_500(self):
        self.client.raise_request_exception = False
        with patch(
            "core.views.Review.objects.count", side_effect=Exception("Database Error")
        ):
            response = self.client.get(self.url)
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
