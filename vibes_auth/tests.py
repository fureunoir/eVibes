from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from graphene.test import Client
from rest_framework.test import APIClient

from core.graphene.schema import schema
from vibes_auth.models import User


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client(schema)
        self.api_client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
        )

    def test_create_user(self):
        query = """
        mutation {
            createUser(email: "newuser@example.com", password: "newpassword", confirmPassword: "newpassword") {
                user {
                    email
                    firstName
                    lastName
                }
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"))
        data = result["data"]["createUser"]["user"]
        self.assertEqual(data["email"], "newuser@example.com")
        self.assertEqual(User.objects.count(), 3)  # Initial two + new user

    def test_obtain_token_view(self):
        url = reverse("token_obtain_pair")
        response = self.api_client.post(url, {"email": self.user.email, "password": "testpassword"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token_view(self):
        obtain_url = reverse("token_obtain_pair")
        refresh_url = reverse("token_refresh")

        # Obtain tokens
        obtain_response = self.api_client.post(obtain_url, {"email": self.user.email, "password": "testpassword"})
        refresh_token = obtain_response.data["refresh"]

        # Refresh tokens
        response = self.api_client.post(refresh_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_verify_token_view(self):
        obtain_url = reverse("token_obtain_pair")
        verify_url = reverse("token_verify")

        # Obtain tokens
        obtain_response = self.api_client.post(obtain_url, {"email": self.user.email, "password": "testpassword"})
        access_token = obtain_response.data["access"]

        # Verify token
        response = self.api_client.post(verify_url, {"token": access_token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["token"], "The token is valid")

    def test_reset_password(self):
        url = reverse("user-reset-password")
        response = self.api_client.post(url, {"email": self.user.email})
        self.assertEqual(response.status_code, 200)

    def test_confirm_password_reset(self):
        url = reverse("user-confirm-password-reset")
        uid = urlsafe_base64_encode(str(self.user.pk).encode()).decode()
        token = PasswordResetTokenGenerator().make_token(self.user)

        response = self.api_client.post(
            url,
            {
                "uidb64": uid,
                "token": token,
                "password": "newpassword",
                "confirm_password": "newpassword",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_upload_avatar(self):
        url = reverse("user-upload-avatar", kwargs={"pk": self.user.pk})
        self.api_client.force_authenticate(user=self.user)

        with open("path/to/avatar.png", "rb") as avatar:
            response = self.api_client.put(url, {"avatar": avatar})
            self.assertEqual(response.status_code, 200)

    def test_activate_user(self):
        url = reverse("user-activate")
        uid = urlsafe_base64_encode(str(self.user.pk).encode()).decode()
        token = PasswordResetTokenGenerator().make_token(self.user)

        response = self.api_client.post(url, {"uidb64": uid, "token": token})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.get(pk=self.user.pk).is_active)
