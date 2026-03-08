from rest_framework import status
from rest_framework.test import APITestCase
from authentication.models import User
from profiles.models import Profile
from unittest.mock import patch


class ProfileTests(APITestCase):
    def setUp(self):
        self.reg_url = "/api/registration/"

        res_b = self.client.post(
            self.reg_url,
            {
                "username": "profile_biz_user",
                "email": "profile_biz@test.de",
                "password": "pass123",
                "repeated_password": "pass123",
                "type": "business",
            },
            format="json",
        )
        self.business_token = res_b.data["token"]
        business_user = User.objects.get(id=res_b.data["user_id"])
        self.business_profile_id = Profile.objects.get(user=business_user).pk

        res_c = self.client.post(
            self.reg_url,
            {
                "username": "profile_cust_user",
                "email": "profile_cust@test.de",
                "password": "pass123",
                "repeated_password": "pass123",
                "type": "customer",
            },
            format="json",
        )
        self.customer_token = res_c.data["token"]
        customer_user = User.objects.get(id=res_c.data["user_id"])
        self.customer_profile_id = Profile.objects.get(user=customer_user).pk

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def tearDown(self):
        self.client.credentials()

    def test_get_profile_authenticated_200(self):
        self.auth(self.business_token)
        response = self.client.get(f"/api/profile/{self.business_profile_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("username", response.data)
        self.assertIn("type", response.data)

    def test_get_profile_fields_are_empty_strings_not_null(self):
        self.auth(self.business_token)
        response = self.client.get(f"/api/profile/{self.business_profile_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            self.assertEqual(response.data.get(field), "", f"Feld '{field}' sollte ein leerer String sein, nicht None.")

    def test_get_profile_unauthenticated_401(self):
        response = self.client.get(f"/api/profile/{self.business_profile_id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_not_found_404(self):
        self.auth(self.business_token)
        response = self.client.get("/api/profile/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_own_profile_200(self):
        self.auth(self.business_token)
        payload = {"first_name": "Max", "location": "Berlin", "tel": "0123456789"}
        response = self.client.patch(f"/api/profile/{self.business_profile_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["location"], "Berlin")
        self.assertEqual(response.data["last_name"], "")

    def test_patch_profile_unauthenticated_401(self):
        self.client.credentials()
        payload = {"first_name": "Max"}
        response = self.client.patch(f"/api/profile/{self.business_profile_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_other_profile_403(self):
        self.auth(self.customer_token)
        payload = {"first_name": "Hacker"}
        response = self.client.patch(f"/api/profile/{self.business_profile_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_not_found_404(self):
        self.auth(self.business_token)
        payload = {"first_name": "Max"}
        response = self.client.patch("/api/profile/999999/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_business_profiles_fields_are_empty_strings_200(self):
        self.auth(self.customer_token)
        response = self.client.get("/api/profiles/business/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if response.data:
            profile = response.data[0]
            self.assertEqual(profile.get("type"), "business")
            for field in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
                self.assertEqual(profile.get(field), "", f"Feld '{field}' sollte ein leerer String sein, nicht None.")

    def test_get_business_profiles_unauthenticated_401(self):
        response = self.client.get("/api/profiles/business/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_business_profiles_server_error_500(self):
        self.auth(self.customer_token)
        with patch('profiles.api.views.ProfileViewSet.get_queryset', side_effect=Exception('DB Error')):
            response = self.client.get("/api/profiles/business/")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_customer_profiles_fields_are_empty_strings_200(self):
        self.auth(self.business_token)
        response = self.client.get("/api/profiles/customer/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if response.data:
            profile = response.data[0]
            self.assertEqual(profile.get("type"), "customer")
            for field in ["first_name", "last_name", "location", "tel"]:
                self.assertEqual(profile.get(field), "", f"Feld '{field}' sollte ein leerer String sein, nicht None.")

    def test_get_customer_profiles_unauthenticated_401(self):
        response = self.client.get("/api/profiles/customer/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_customer_profiles_server_error_500(self):
        self.auth(self.business_token)
        with patch('profiles.api.views.ProfileViewSet.get_queryset', side_effect=Exception('DB Error')):
            response = self.client.get("/api/profiles/customer/")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_profile_server_error_500(self):
        self.auth(self.business_token)
        with patch('profiles.api.views.ProfileViewSet.get_object', side_effect=Exception('DB Error')):
            response = self.client.get(f"/api/profile/{self.business_profile_id}/")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_patch_profile_server_error_500(self):
        self.auth(self.business_token)
        with patch('profiles.api.views.ProfileViewSet.get_object', side_effect=Exception('DB Error')):
            response = self.client.patch(f"/api/profile/{self.business_profile_id}/", {}, format="json")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_business_profiles_server_error_500(self):
        self.auth(self.customer_token)
        with patch('profiles.api.views.ProfileViewSet.get_queryset', side_effect=Exception('DB Error')):
            response = self.client.get("/api/profiles/business/")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_customer_profiles_server_error_500(self):
        self.auth(self.business_token)
        with patch('profiles.api.views.ProfileViewSet.get_queryset', side_effect=Exception('DB Error')):
            response = self.client.get("/api/profiles/customer/")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
