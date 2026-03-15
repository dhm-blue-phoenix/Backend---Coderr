from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail


class OrdersTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        reg_url = "/api/registration/"

        res_b = self.client.post(
            reg_url,
            {
                "username": "order_biz",
                "email": "order_biz@test.de",
                "password": "pass123",
                "repeated_password": "pass123",
                "type": "business",
            },
            format="json",
        )
        self.business_token = res_b.data["token"]
        self.business_user = User.objects.get(id=res_b.data["user_id"])

        res_c = self.client.post(
            reg_url,
            {
                "username": "order_cust",
                "email": "order_cust@test.de",
                "password": "pass123",
                "repeated_password": "pass123",
                "type": "customer",
            },
            format="json",
        )
        self.customer_token = res_c.data["token"]
        self.customer_user = User.objects.get(id=res_c.data["user_id"])

        self.offer = Offer.objects.create(
            creator=self.business_user, title="Web Development", description="..."
        )

        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Package",
            price=150,
            delivery_time_in_days=5,
            revisions=3,
            features=["Logo Design", "Visitenkarten"],
            offer_type="basic",
        )

        self.second_offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Aut in in.",
            price=250,
            delivery_time_in_days=10,
            revisions=5,
            features=["Alles"],
            offer_type="premium",
        )

        self.auth(self.customer_token)
        order_res = self.client.post(
            "/api/orders/",
            {"offer_detail_id": self.offer_detail.id},
            format="json",
        )
        self.order_id = order_res.data["id"]
        self.client.credentials()

        self.admin_user = User.objects.create_superuser(
            username="admin_orders", password="adminpass", email="admin_orders@test.de"
        )
        self.admin_token = Token.objects.create(user=self.admin_user).key

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_list_orders_as_customer_200(self):
        self.auth(self.customer_token)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

        order_data = response.data[0]
        self.assertEqual(order_data["id"], self.order_id)
        self.assertEqual(order_data["customer_user"], self.customer_user.id)
        self.assertEqual(order_data["business_user"], self.business_user.id)

    def test_list_orders_as_business_200(self):
        self.auth(self.business_token)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

    def test_list_orders_unauthenticated_401(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_orders_response_structure(self):
        self.auth(self.customer_token)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertGreater(len(response.data), 0)

        for order in response.data:
            self.assertIn("id", order)
            self.assertIn("customer_user", order)
            self.assertIn("business_user", order)
            self.assertIn("title", order)
            self.assertIn("price", order)
            self.assertIn("status", order)
            self.assertIn("created_at", order)
            self.assertIn("updated_at", order)
            self.assertIn("revisions", order)
            self.assertIn("delivery_time_in_days", order)
            self.assertIn("features", order)
            self.assertIn("offer_type", order)

    def test_create_order_as_customer_201(self):
        self.auth(self.customer_token)
        response = self.client.post(
            "/api/orders/", {"offer_detail_id": self.offer_detail.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "in_progress")
        self.assertEqual(response.data["customer_user"], self.customer_user.id)

    def test_create_order_unauthenticated_401(self):
        response = self.client.post(
            "/api/orders/", {"offer_detail_id": self.offer_detail.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_as_business_403(self):
        self.auth(self.business_token)
        response = self.client.post(
            "/api/orders/", {"offer_detail_id": self.offer_detail.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_missing_offer_detail_400(self):
        self.auth(self.customer_token)
        response = self.client.post("/api/orders/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_offer_detail_not_found_404(self):
        self.auth(self.customer_token)
        response = self.client.post(
            "/api/orders/", {"offer_detail_id": 999999}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_with_invalid_id_string_400(self):
        self.auth(self.customer_token)
        response = self.client.post(
            "/api/orders/", {"offer_detail_id": "invalid_id"}, format="json"
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )

    def test_patch_order_unauthenticated_401(self):
        response = self.client.patch(
            f"/api/orders/{self.order_id}/", {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_order_status_as_business_200(self):
        self.auth(self.business_token)
        response = self.client.patch(
            f"/api/orders/{self.order_id}/", {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    def test_patch_order_status_as_customer_403(self):
        self.auth(self.customer_token)
        response = self.client.patch(
            f"/api/orders/{self.order_id}/", {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_order_not_found_404(self):
        self.auth(self.business_token)
        response = self.client.patch(
            "/api/orders/999999/", {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_order_with_invalid_id_string_400(self):
        self.auth(self.business_token)
        response = self.client.patch(
            "/api/orders/invalid_id/", {"status": "completed"}, format="json"
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )

    def test_delete_order_with_invalid_id_string_400(self):
        self.auth(self.admin_token)
        response = self.client.delete("/api/orders/invalid_id/")
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )

    def test_patch_order_invalid_status_400(self):
        self.auth(self.business_token)
        response = self.client.patch(
            f"/api/orders/{self.order_id}/", {"status": "invalid_status"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_order_valid_status_transitions(self):
        self.auth(self.business_token)

        valid_statuses = ["in_progress", "completed", "cancelled"]

        for status_value in valid_statuses:
            response = self.client.patch(
                f"/api/orders/{self.order_id}/", {"status": status_value}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["status"], status_value)

    def test_delete_order_unauthenticated_401(self):
        response = self.client.delete(f"/api/orders/{self.order_id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_as_admin_204(self):
        self.auth(self.admin_token)
        response = self.client.delete(f"/api/orders/{self.order_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_order_as_non_admin_403(self):
        self.auth(self.business_token)
        response = self.client.delete(f"/api/orders/{self.order_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_not_found_404(self):
        self.auth(self.admin_token)
        response = self.client.delete("/api/orders/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_count_unauthenticated_401(self):
        response = self.client.get(f"/api/order-count/{self.business_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_count_200(self):
        self.auth(self.customer_token)
        response = self.client.get(f"/api/order-count/{self.business_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 1)

    def test_order_count_excludes_completed(self):
        self.auth(self.business_token)
        self.client.patch(f"/api/orders/{self.order_id}/", {"status": "completed"})

        self.auth(self.customer_token)
        response = self.client.get(f"/api/order-count/{self.business_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 0)

    def test_order_count_excludes_cancelled(self):
        self.auth(self.business_token)
        self.client.patch(f"/api/orders/{self.order_id}/", {"status": "cancelled"})

        self.auth(self.customer_token)
        response = self.client.get(f"/api/order-count/{self.business_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 0)

    def test_order_count_not_found_404(self):
        self.auth(self.customer_token)
        response = self.client.get("/api/order-count/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_count_with_invalid_id_string_400(self):
        self.auth(self.customer_token)
        response = self.client.get("/api/order-count/invalid_id/")
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )

    def test_completed_order_count_unauthenticated_401(self):
        response = self.client.get(
            f"/api/completed-order-count/{self.business_user.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_completed_order_count_200(self):
        self.auth(self.business_token)
        self.client.patch(f"/api/orders/{self.order_id}/", {"status": "completed"})
        response = self.client.get(
            f"/api/completed-order-count/{self.business_user.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 1)

    def test_completed_order_count_not_found_404(self):
        self.auth(self.business_token)
        response = self.client.get("/api/completed-order-count/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_order_count_with_invalid_id_string_400(self):
        self.auth(self.business_token)
        response = self.client.get("/api/completed-order-count/invalid_id/")
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )

    def test_list_orders_server_error_500(self):
        self.auth(self.customer_token)
        self.client.raise_request_exception = False
        with patch(
            "orders_app.api.views.OrderViewSet.get_queryset",
            side_effect=Exception("Database Error"),
        ):
            response = self.client.get("/api/orders/")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_create_order_server_error_500(self):
        self.auth(self.customer_token)
        self.client.raise_request_exception = False
        with patch(
            "orders_app.models.Order.objects.create",
            side_effect=Exception("Database Error"),
        ):
            response = self.client.post(
                "/api/orders/", {"offer_detail_id": self.offer_detail.id}, format="json"
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_patch_order_server_error_500(self):
        self.auth(self.business_token)
        self.client.raise_request_exception = False
        with patch(
            "orders_app.api.views.OrderViewSet.get_object",
            side_effect=Exception("Database Error"),
        ):
            response = self.client.patch(
                f"/api/orders/{self.order_id}/", {"status": "completed"}, format="json"
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_delete_order_server_error_500(self):
        self.auth(self.admin_token)
        self.client.raise_request_exception = False
        with patch(
            "orders_app.api.views.OrderViewSet.get_object",
            side_effect=Exception("Database Error"),
        ):
            response = self.client.delete(f"/api/orders/{self.order_id}/")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_order_count_server_error_500(self):
        self.auth(self.customer_token)
        self.client.raise_request_exception = False
        with patch(
            "orders_app.models.Order.objects.filter",
            side_effect=Exception("Database Error"),
        ):
            response = self.client.get(f"/api/order-count/{self.business_user.id}/")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_completed_order_count_server_error_500(self):
        self.auth(self.business_token)
        self.client.raise_request_exception = False
        with patch(
            "orders_app.models.Order.objects.filter",
            side_effect=Exception("Database Error"),
        ):
            response = self.client.get(
                f"/api/completed-order-count/{self.business_user.id}/"
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_patch_order_not_found_returns_404_not_403(self):
        self.auth(self.business_token)
        response = self.client.patch("/api/orders/999951/", {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_order_has_correct_title(self):
        self.auth(self.customer_token)
        response = self.client.post(
            "/api/orders/", {"offer_detail_id": self.second_offer_detail.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Aut in in.")

    def test_get_order_customer_has_correct_title(self):
        self.auth(self.customer_token)
        self.client.post(
            "/api/orders/", {"offer_detail_id": self.second_offer_detail.id}, format="json"
        )
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [o["title"] for o in response.data]
        self.assertIn("Aut in in.", titles)

    def test_get_order_business_has_correct_title(self):
        self.auth(self.customer_token)
        self.client.post(
            "/api/orders/", {"offer_detail_id": self.second_offer_detail.id}, format="json"
        )
        self.auth(self.business_token)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [o["title"] for o in response.data]
        self.assertIn("Aut in in.", titles)

    def test_patch_order_has_correct_title(self):
        self.auth(self.customer_token)
        order_res = self.client.post(
            "/api/orders/", {"offer_detail_id": self.second_offer_detail.id}, format="json"
        )
        order_id = order_res.data["id"]
        self.auth(self.business_token)
        response = self.client.patch(
            f"/api/orders/{order_id}/", {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Aut in in.")
