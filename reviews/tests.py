from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


User = get_user_model()


class ReviewsTests(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            username='review_customer',
            email='review_customer@test.de',
            password='password123',
            type='customer'
        )
        self.business_user = User.objects.create_user(
            username='review_business',
            email='review_business@test.de',
            password='password123',
            type='business'
        )
        self.another_customer = User.objects.create_user(
            username='review_customer2',
            email='review_customer2@test.de',
            password='password123',
            type='customer'
        )
        self.client.force_authenticate(user=self.customer_user)
        review_data = {
            'business_user': self.business_user.id,
            'rating': 4,
            'description': 'This is a test review'
        }
        review_res = self.client.post("/api/reviews/", review_data)
        self.assertEqual(review_res.status_code, status.HTTP_201_CREATED)
        self.review_id = review_res.data['id']

    def test_list_reviews_unauthenticated_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/reviews/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_reviews_authenticated_200(self):
        self.client.force_authenticate(user=self.customer_user)
        res = self.client.get("/api/reviews/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)

    def test_list_reviews_filters_and_ordering(self):
        self.client.force_authenticate(user=self.another_customer)
        second_review_data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'This is another test review'
        }
        res = self.client.post("/api/reviews/", second_review_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        second_review_id = res.data['id']
        self.client.force_authenticate(user=self.customer_user)
        
        res = self.client.get(f"/api/reviews/?business_user_id={self.business_user.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        res = self.client.get(f"/api/reviews/?reviewer_id={self.another_customer.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], second_review_id)

        res = self.client.get("/api/reviews/?ordering=-rating")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['rating'], 5)
        self.assertEqual(res.data[1]['rating'], 4)

    def test_create_review_unauthenticated_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.post("/api/reviews/", {'business_user': self.business_user.id, 'rating': 4, 'description': 'Test'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_business_user_403(self):
        self.client.force_authenticate(user=self.business_user)
        res = self.client.post("/api/reviews/", {'business_user': self.customer_user.id, 'rating': 3, 'description': 'fails'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_duplicate_400(self):
        self.client.force_authenticate(user=self.customer_user)
        duplicate_data = {'business_user': self.business_user.id, 'rating': 2, 'description': 'A second try'}
        res = self.client.post("/api/reviews/", duplicate_data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_rating_400(self):
        self.client.force_authenticate(user=self.another_customer)
        invalid_data = {'business_user': self.business_user.id, 'rating': 10, 'description': 'Invalid rating'}
        res = self.client.post("/api/reviews/", invalid_data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_rating_range(self):
        self.client.force_authenticate(user=self.another_customer)
        response = self.client.post(
            "/api/reviews/",
            {'business_user': self.business_user.id, 'rating': 0, 'description': 'Too low'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        temp_customer1 = User.objects.create_user(
            username='temp_customer_high',
            email='temp_high@test.de',
            password='test123',
            type='customer'
        )
        self.client.force_authenticate(user=temp_customer1)
        response = self.client.post(
            "/api/reviews/",
            {'business_user': self.business_user.id, 'rating': 6, 'description': 'Too high'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        for rating in range(1, 6):
            temp_customer = User.objects.create_user(
                username=f'temp_customer_{rating}',
                email=f'temp_{rating}@test.de',
                password='test123',
                type='customer'
            )
            self.client.force_authenticate(user=temp_customer)
            response = self.client.post(
                "/api/reviews/",
                {'business_user': self.business_user.id, 'rating': rating, 'description': f'Rating {rating}'}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['rating'], rating)

    def test_patch_review_unauthenticated_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.patch(f"/api/reviews/{self.review_id}/", {'rating': 5})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_own_review_200(self):
        self.client.force_authenticate(user=self.customer_user)
        res = self.client.patch(f"/api/reviews/{self.review_id}/", {'rating': 5, 'description': 'Updated'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['rating'], 5)
        self.assertEqual(res.data['description'], 'Updated')

    def test_patch_review_other_user_403(self):
        self.client.force_authenticate(user=self.another_customer)
        res = self.client.patch(f"/api/reviews/{self.review_id}/", {'rating': 1})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_not_found_404(self):
        self.client.force_authenticate(user=self.customer_user)
        res = self.client.patch("/api/reviews/999999/", {'rating': 5})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_review_unauthenticated_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.delete(f"/api/reviews/{self.review_id}/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_own_review_204(self):
        self.client.force_authenticate(user=self.customer_user)
        res = self.client.delete(f"/api/reviews/{self.review_id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_review_other_user_403(self):
        self.client.force_authenticate(user=self.another_customer)
        res = self.client.delete(f"/api/reviews/{self.review_id}/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_not_found_404(self):
        self.client.force_authenticate(user=self.customer_user)
        res = self.client.delete("/api/reviews/999999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_reviews_server_error_500(self):
        self.client.force_authenticate(user=self.customer_user)
        self.client.raise_request_exception = False
        with patch('reviews.api.views.ReviewViewSet.get_queryset', side_effect=Exception('Database Error')):
            res = self.client.get("/api/reviews/")
            self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_create_review_server_error_500(self):
        self.client.force_authenticate(user=self.another_customer)
        self.client.raise_request_exception = False
        with patch('reviews.models.Review.objects.create', side_effect=Exception('Database Error')):
            res = self.client.post(
                "/api/reviews/",
                {'business_user': self.business_user.id, 'rating': 4, 'description': 'Test'}
            )
            self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_patch_review_server_error_500(self):
        self.client.force_authenticate(user=self.customer_user)
        self.client.raise_request_exception = False
        with patch('reviews.api.views.ReviewViewSet.get_object', side_effect=Exception('Database Error')):
            res = self.client.patch(
                f"/api/reviews/{self.review_id}/",
                {'rating': 5}
            )
            self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_delete_review_server_error_500(self):
        self.client.force_authenticate(user=self.customer_user)
        self.client.raise_request_exception = False
        with patch('reviews.api.views.ReviewViewSet.get_object', side_effect=Exception('Database Error')):
            res = self.client.delete(f"/api/reviews/{self.review_id}/")
            self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
