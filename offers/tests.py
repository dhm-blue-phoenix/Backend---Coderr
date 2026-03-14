from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from authentication.models import User
from unittest.mock import patch


OFFER_DETAILS_PAYLOAD = [
    {
        "title": "Basic Design",
        "revisions": 2,
        "delivery_time_in_days": 5,
        "price": 100,
        "features": ["Logo Design", "Visitenkarte"],
        "offer_type": "basic",
    },
    {
        "title": "Standard Design",
        "revisions": 5,
        "delivery_time_in_days": 7,
        "price": 200,
        "features": ["Logo Design", "Visitenkarte", "Briefpapier"],
        "offer_type": "standard",
    },
    {
        "title": "Premium Design",
        "revisions": 10,
        "delivery_time_in_days": 10,
        "price": 500,
        "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
        "offer_type": "premium",
    },
]


class OffersTests(APITestCase):
    def setUp(self):
        reg_url = "/api/registration/"

        res_b = self.client.post(reg_url, {
            "username": "offerbiz",
            "email": "offerbiz@test.de",
            "password": "pass123",
            "repeated_password": "pass123",
            "type": "business",
        }, format="json")
        self.assertEqual(res_b.status_code, status.HTTP_201_CREATED)
        self.business_token = res_b.data["token"]
        self.business_user_id = res_b.data["user_id"]
        self.business_user = User.objects.get(id=self.business_user_id)

        res_c = self.client.post(reg_url, {
            "username": "offercust",
            "email": "offercust@test.de",
            "password": "pass123",
            "repeated_password": "pass123",
            "type": "customer",
        }, format="json")
        self.assertEqual(res_c.status_code, status.HTTP_201_CREATED)
        self.customer_token = res_c.data["token"]

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def tearDown(self):
        self.client.credentials()

    def create_offer(self, token, title="Test Offer"):
        self.auth(token)
        response = self.client.post(
            "/api/offers/",
            {
                "title": title,
                "description": "Test Description",
                "details": OFFER_DETAILS_PAYLOAD,
            },
            format="json",
        )
        return response
        

    def test_list_offers_no_auth_200(self):
        self.create_offer(self.business_token)
        self.client.credentials()
        response = self.client.get("/api/offers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_offers_pagination_structure(self):
        self.create_offer(self.business_token)
        self.client.credentials()
        response = self.client.get("/api/offers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

    def test_list_offers_page_size(self):
        for i in range(3):
            self.create_offer(self.business_token, title=f"Offer {i}")

        self.client.credentials()
        response = self.client.get("/api/offers/?page_size=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_offers_filter_by_creator_id(self):
        self.create_offer(self.business_token)
        self.client.credentials()
        response = self.client.get(
            f"/api/offers/?creator_id={self.business_user_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", [])
        self.assertGreater(len(results), 0)
        for offer in results:
            self.assertEqual(offer["user_details"]["id"], self.business_user_id)

    def test_create_offer_business_201(self):
        response = self.create_offer(self.business_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(len(response.data["details"]), 3)
        # Validate details array contains proper objects, not URLs
        for detail in response.data["details"]:
            self.assertIn("id", detail)
            self.assertIn("title", detail)
            self.assertIn("price", detail)
            self.assertIn("delivery_time_in_days", detail)
            self.assertIn("revisions", detail)
            self.assertIn("features", detail)
            self.assertIn("offer_type", detail)

    def test_create_offer_customer_403(self):
        response = self.create_offer(self.customer_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_create_offer_invalid_details_count_400(self):
        self.auth(self.business_token)
        
        less_details = OFFER_DETAILS_PAYLOAD[:2]
        payload_less = {
            "title": "Zu wenige Details",
            "description": "Test",
            "details": less_details
        }
        response_less = self.client.post("/api/offers/", payload_less, format="json")
        self.assertEqual(response_less.status_code, status.HTTP_400_BAD_REQUEST, "Sollte bei < 3 Details fehlschlagen.")

        more_details = OFFER_DETAILS_PAYLOAD * 2
        payload_more = {
            "title": "Zu viele Details",
            "description": "Test",
            "details": more_details
        }
        response_more = self.client.post("/api/offers/", payload_more, format="json")
        self.assertEqual(response_more.status_code, status.HTTP_400_BAD_REQUEST, "Sollte bei > 3 Details fehlschlagen.")


    def test_get_offer_detail_authenticated_200(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.auth(self.customer_token)
        response = self.client.get(f"/api/offers/{offer_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("details", response.data)
        self.assertIn("user", response.data)
        self.assertIn("title", response.data)
        self.assertIn("description", response.data)
        self.assertIn("min_price", response.data)
        self.assertIn("min_delivery_time", response.data)
        # Validate details structure
        self.assertIsInstance(response.data["details"], list)
        self.assertEqual(len(response.data["details"]), 3)
        for detail in response.data["details"]:
            self.assertIn("id", detail)
            self.assertIn("url", detail)

    def test_get_offer_detail_unauthenticated_401(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.client.credentials()
        response = self.client.get(f"/api/offers/{offer_id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offer_detail_not_found_404(self):
        self.auth(self.business_token)
        response = self.client.get("/api/offers/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_offer_detail_has_detail_urls(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.auth(self.customer_token)
        response = self.client.get(f"/api/offers/{offer_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        details = response.data.get("details", [])
        self.assertGreater(len(details), 0)
        for detail in details:
            self.assertIn("url", detail)
            self.assertIn("id", detail)


    def test_delete_offer_owner_204(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.auth(self.business_token)
        response = self.client.delete(f"/api/offers/{offer_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_offer_non_owner_403(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.auth(self.customer_token)
        response = self.client.delete(f"/api/offers/{offer_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_unauthenticated_401(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.client.credentials()
        response = self.client.delete(f"/api/offers/{offer_id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_offer_not_found_404(self):
        self.auth(self.business_token)
        response = self.client.delete("/api/offers/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_list_offers_filter_by_min_price(self):
        self.create_offer(self.business_token, title="Offer 1")
        self.client.credentials()
        
        response_all = self.client.get("/api/offers/")
        self.assertEqual(response_all.status_code, status.HTTP_200_OK)
        
        min_price = 200
        response_filtered = self.client.get(f"/api/offers/?min_price={min_price}")
        self.assertEqual(response_filtered.status_code, status.HTTP_200_OK)
        
        for offer in response_filtered.data.get("results", []):
            self.assertGreaterEqual(offer.get("min_price", 0), min_price)

    def test_list_offers_filter_by_max_delivery_time(self):
        self.create_offer(self.business_token, title="Offer 1")
        self.client.credentials()
        
        response = self.client.get("/api/offers/?max_delivery_time=7")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for offer in response.data.get("results", []):
            self.assertLessEqual(offer.get("min_delivery_time", 0), 7)

    def test_list_offers_ordering_by_updated_at(self):
        self.create_offer(self.business_token, title="Offer 1")
        self.create_offer(self.business_token, title="Offer 2")
        self.client.credentials()
        
        response = self.client.get("/api/offers/?ordering=updated_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data.get("results", [])), 0)

    def test_list_offers_ordering_by_min_price(self):
        self.create_offer(self.business_token, title="Offer 1")
        self.create_offer(self.business_token, title="Offer 2")
        self.client.credentials()
        
        response = self.client.get("/api/offers/?ordering=min_price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data.get("results", [])
        if len(results) > 1:
            prices = [offer.get("min_price", 0) for offer in results]
            self.assertTrue(prices == sorted(prices) or prices == sorted(prices, reverse=True))

    def test_list_offers_search_by_title(self):
        self.create_offer(self.business_token, title="Website Design Service")
        self.client.credentials()
        
        response = self.client.get("/api/offers/?search=Website")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data.get("results", [])
        self.assertGreater(len(results), 0)
        
        found = any("Website" in offer.get("title", "") or "Website" in offer.get("description", "") 
                   for offer in results)
        self.assertTrue(found, "Search sollte in title oder description suchen")


    def test_patch_own_offer_details_200(self):
        self.auth(self.business_token)
        response = self.client.post(
            "/api/offers/",
            {
                "title": "Test Offer",
                "description": "Test Description",
                "details": OFFER_DETAILS_PAYLOAD,
            },
            format="json",
        )
        if response.status_code != 201:
            self.skipTest(f"Angebot kann nicht erstellt werden: {response.data}")
            return
            
        offer_id = response.data['id']
        self.auth(self.business_token)
        payload = {
            "details": [
                {
                    "offer_type": "basic",
                    "price": 120,
                }
            ]
        }
        response = self.client.patch(
            f"/api/offers/{offer_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_offer_unauthenticated_401(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.client.credentials()
        payload = {"title": "Updated Title"}
        response = self.client.patch(f"/api/offers/{offer_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_offer_non_owner_403(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.auth(self.customer_token)
        payload = {"title": "Hacked Title"}
        response = self.client.patch(f"/api/offers/{offer_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_offer_not_found_404(self):
        self.auth(self.business_token)
        payload = {"title": "Updated"}
        response = self.client.patch("/api/offers/999999/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_invalid_details_400(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.auth(self.business_token)
        payload = {
            "details": [
                {
                    "offer_type": "invalid_type",
                    "price": 100,
                }
            ]
        }
        response = self.client.patch(f"/api/offers/{offer_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_offer_missing_type_400(self):
        """Test that PATCH without offer_type returns 400"""
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.auth(self.business_token)
        payload = {
            "details": [
                {
                    "price": 150,
                    # Missing "offer_type" - should return 400
                }
            ]
        }
        response = self.client.patch(f"/api/offers/{offer_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_offer_server_error_500(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.auth(self.business_token)
        self.client.raise_request_exception = False
        with patch('offers.api.views.OfferViewSet.get_object', side_effect=Exception('Database Error')):
            response = self.client.patch(f"/api/offers/{offer_id}/", {"title": "Test"}, format="json")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_offerdetails_authenticated_200(self):
        offer_res = self.create_offer(self.business_token)
        details = offer_res.data['details']
        if not details:
            self.skipTest("Keine Offer Details vorhanden")
            return
        
        detail_id = details[0]['id']
        self.auth(self.customer_token)
        response = self.client.get(f"/api/offerdetails/{detail_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("title", response.data)
        self.assertIn("price", response.data)
        self.assertIn("delivery_time_in_days", response.data)
        self.assertIn("revisions", response.data)
        self.assertIn("features", response.data)
        self.assertIn("offer_type", response.data)
        # Validate correct values from creation
        self.assertEqual(response.data["title"], OFFER_DETAILS_PAYLOAD[0]["title"])
        self.assertEqual(response.data["price"], OFFER_DETAILS_PAYLOAD[0]["price"])
        self.assertEqual(response.data["offer_type"], OFFER_DETAILS_PAYLOAD[0]["offer_type"])

    def test_get_offerdetails_unauthenticated_401(self):
        offer_res = self.create_offer(self.business_token)
        details = offer_res.data['details']
        if not details:
            self.skipTest("Keine Offer Details vorhanden")
            return
        
        detail_id = details[0]['id']
        self.client.credentials()
        response = self.client.get(f"/api/offerdetails/{detail_id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offerdetails_not_found_404(self):
        self.auth(self.business_token)
        response = self.client.get("/api/offerdetails/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_offerdetails_invalid_id_string_400(self):
        """Test that invalid offerdetail ID (string) returns 400 or 404, not 500"""
        self.auth(self.customer_token)
        response = self.client.get("/api/offerdetails/invalid_id/")
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_get_offerdetails_server_error_500(self):
        offer_res = self.create_offer(self.business_token)
        details = offer_res.data['details']
        if not details:
            self.skipTest("Keine Offer Details vorhanden")
            return
        
        detail_id = details[0]['id']
        self.auth(self.business_token)
        self.client.raise_request_exception = False
        with patch('offers.api.views.OfferDetailViewSet.get_object', side_effect=Exception('Database Error')):
            response = self.client.get(f"/api/offerdetails/{detail_id}/")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_list_offers_server_error_500(self):
        self.client.credentials()
        self.client.raise_request_exception = False
        with patch('offers.api.views.OfferViewSet.get_queryset', side_effect=Exception('Database Error')):
            response = self.client.get("/api/offers/")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_create_offer_server_error_500(self):
        self.auth(self.business_token)
        self.client.raise_request_exception = False
        with patch('offers.models.Offer.objects.create', side_effect=Exception('Database Error')):
            response = self.client.post(
                "/api/offers/",
                {
                    "title": "Test Offer",
                    "description": "Test Description",
                    "details": OFFER_DETAILS_PAYLOAD,
                },
                format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_offer_detail_server_error_500(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.auth(self.customer_token)
        self.client.raise_request_exception = False
        with patch('offers.api.views.OfferViewSet.get_object', side_effect=Exception('Database Error')):
            response = self.client.get(f"/api/offers/{offer_id}/")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_delete_offer_server_error_500(self):
        offer_res = self.create_offer(self.business_token)
        offer_id = offer_res.data['id']
        
        self.auth(self.business_token)
        self.client.raise_request_exception = False
        with patch('offers.api.views.OfferViewSet.get_object', side_effect=Exception('Database Error')):
            response = self.client.delete(f"/api/offers/{offer_id}/")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_offer_with_invalid_id_string_400(self):
        """Test that invalid offer ID (string) returns 400, not 500"""
        self.auth(self.customer_token)
        response = self.client.get("/api/offers/invalid_id/")
        # Should return 400 or 404, not 500
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_delete_offer_with_invalid_id_string_400(self):
        """Test that DELETE with invalid offer ID (string) returns 400, not 500"""
        self.auth(self.business_token)
        response = self.client.delete("/api/offers/invalid_id/")
        # Should return 400 or 404, not 500
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_patch_offer_with_invalid_id_string_400(self):
        """Test that PATCH with invalid offer ID (string) returns 400, not 500"""
        self.auth(self.business_token)
        response = self.client.patch("/api/offers/invalid_id/", {"title": "Updated"}, format="json")
        # Should return 400 or 404, not 500
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])
