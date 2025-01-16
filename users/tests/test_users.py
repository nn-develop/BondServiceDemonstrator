from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


class UserTests(TestCase):
    def setUp(self) -> None:
        # Set up the test api_client and initial user
        self.api_client: APIClient = APIClient()
        self.user: User = User.objects.create_user(
            username="testuser", password="password"
        )
        self.token: Token = Token.objects.create(user=self.user)

    def test_user_registration_creates_user(self) -> None:
        # Test user registration
        registration_data: dict[str, str] = {
            "username": "newuser",
            "password": "newpassword",
            "email": "newuser@example.com",
        }
        response: Response = self.api_client.post(
            "/api/users/register/", registration_data, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 2)

    def test_user_registration_with_missing_fields(self) -> None:
        # Test registration with missing fields
        incomplete_data: dict[str, str] = {
            "username": "newuser",
        }
        response: Response = self.api_client.post(
            "/api/users/register/", incomplete_data, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_user_login(self) -> None:
        # Test user login (authentication using Token)
        login_data: dict[str, str] = {
            "username": "testuser",
            "password": "password",
        }
        response: Response = self.api_client.post(
            "/api/users/login/", login_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_user_login_invalid_credentials(self) -> None:
        # Test login with invalid credentials
        invalid_data: dict[str, str] = {
            "username": "testuser",
            "password": "wrongpassword",
        }
        response: Response = self.api_client.post(
            "/api/users/login/", invalid_data, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_user_logout(self) -> None:
        # Test user logout (use standard DRF LogoutView)
        self.api_client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response: Response = self.api_client.post("/api/users/logout/")
        self.assertEqual(response.status_code, 200)

    def test_user_logout_without_token(self) -> None:
        # Test logout without token
        response: Response = self.api_client.post("/api/users/logout/")
        self.assertEqual(response.status_code, 401)
