from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from auth_app.models import User
from unittest.mock import patch


class AuthenticationTests(APITestCase):
    
    def setUp(self):
        self.registration_url = reverse("register")
        self.login_url = reverse("login")

        self.customer_payload = {
            "username": "customer",
            "email": "customer@test.de",
            "password": "a_secure_password",
            "repeated_password": "a_secure_password",
            "type": "customer",
        }

        self.business_payload = {
            "username": "business",
            "email": "business@test.de",
            "password": "a_secure_password",
            "repeated_password": "a_secure_password",
            "type": "business",
        }

    def test_registration_customer_success_201(self):
        response = self.client.post(
            self.registration_url, self.customer_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)
        self.assertEqual(response.data["email"], self.customer_payload["email"])

    def test_registration_missing_fields_400(self):
        payload = self.customer_payload.copy()
        del payload["email"]
        response = self.client.post(self.registration_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_missing_username_400(self):
        payload = self.customer_payload.copy()
        del payload["username"]
        response = self.client.post(self.registration_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_registration_missing_password_400(self):
        payload = self.customer_payload.copy()
        del payload["password"]
        response = self.client.post(self.registration_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_password_mismatch_400(self):
        payload = self.customer_payload.copy()
        payload["repeated_password"] = "wrong_password"
        response = self.client.post(self.registration_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_duplicate_email_400(self):
        self.client.post(self.registration_url, self.customer_payload, format="json")
        response = self.client.post(
            self.registration_url, self.customer_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_duplicate_username_400(self):
        self.client.post(self.registration_url, self.customer_payload, format="json")
        payload = self.business_payload.copy()
        payload["username"] = self.customer_payload["username"]
        response = self.client.post(self.registration_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_login_success_200(self):
        self.client.post(self.registration_url, self.customer_payload, format="json")
        login_payload = {
            "username": self.customer_payload["username"],
            "password": self.customer_payload["password"],
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], login_payload["username"])

    def test_login_wrong_credentials_400(self):
        login_payload = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_username_400(self):
        login_payload = {"password": "examplePassword"}
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password_400(self):
        login_payload = {"username": "exampleUsername"}
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_request_success(self):
        reg_response = self.client.post(self.registration_url, self.business_payload, format="json")
        token = reg_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        protected_url = "/api/offers/"
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_registration_business_success_201(self):
        response = self.client.post(
            self.registration_url, self.business_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)
        self.assertEqual(response.data["email"], self.business_payload["email"])

    def test_registration_server_error_500(self):
        self.client.raise_request_exception = False
        with patch('auth_app.models.User.objects.create_user', side_effect=Exception('Database Error')):
            response = self.client.post(
                self.registration_url, self.customer_payload, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_login_server_error_500(self):
        self.client.post(self.registration_url, self.customer_payload, format="json")
        login_payload = {
            "username": self.customer_payload["username"],
            "password": self.customer_payload["password"],
        }
        self.client.raise_request_exception = False
        with patch('auth_app.models.User.objects.get', side_effect=Exception('Database Error')):
            response = self.client.post(self.login_url, login_payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
