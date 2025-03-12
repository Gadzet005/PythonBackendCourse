from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from users.factories import UserFactory
from django.contrib.auth.models import User


class UsersTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.client = APIClient()
        cls.auth_client = APIClient()
        cls.auth_client.force_authenticate(user=cls.user)

    def test_user_registration(self):
        response = self.client.post(
            "/api/users/",
            {
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "password123",
            },
        )

        user = User.objects.get(username="testuser")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.email, "testuser@example.com")

    def test_user_registration_with_existing_username(self):
        UserFactory.create(username="testuser")

        response = self.client.post(
            "/api/users/",
            {
                "username": "testuser",
                "email": "testuser2@example.com",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_details(self):
        response = self.auth_client.get(f"/api/users/{self.user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], self.user.username)
        self.assertEqual(response.json()["email"], self.user.email)
