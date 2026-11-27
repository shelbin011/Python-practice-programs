from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase


class JWTAuthenticationTests(APITestCase):
    signup_url = "/api/auth/signup/"
    login_url = "/api/auth/login/"
    logout_url = "/api/auth/logout/"
    refresh_url = "/api/auth/refresh/"
    protected_url = "/api/jobs/"

    def signup(self):
        response = self.client.post(
            self.signup_url,
            {
                "name": "Test Candidate",
                "email": "candidate@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assert_success_response(response)
        return response

    def login(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "candidate@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_success_response(response)
        return response

    def assert_success_response(self, response):
        self.assertEqual(response.data["success"], True)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)

    def assert_error_response(self, response):
        self.assertEqual(response.data["success"], False)
        self.assertIn("message", response.data)
        self.assertIn("errors", response.data)

    def test_signup_hashes_password_and_assigns_default_group(self):
        response = self.signup()
        user = User.objects.get(email="candidate@example.com")

        self.assertTrue(user.check_password("StrongPassword123!"))
        self.assertFalse(user.password == "StrongPassword123!")
        self.assertTrue(Group.objects.get(name="Candidate") in user.groups.all())
        self.assertEqual(response.data["data"]["email"], "candidate@example.com")

    def test_duplicate_email_is_rejected(self):
        self.signup()
        response = self.client.post(
            self.signup_url,
            {
                "name": "Another Candidate",
                "email": "CANDIDATE@example.com",
                "password": "AnotherStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_error_response(response)

    def test_login_returns_tokens_and_public_user_data(self):
        self.signup()
        response = self.login()

        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["email"], "candidate@example.com")
        self.assertNotIn("password", response.data["data"]["user"])

    def test_invalid_and_inactive_login_are_rejected(self):
        self.signup()
        invalid_response = self.client.post(
            self.login_url,
            {"email": "candidate@example.com", "password": "wrong-password"},
            format="json",
        )
        self.assertEqual(
            invalid_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assert_error_response(invalid_response)

        user = User.objects.get(email="candidate@example.com")
        user.is_active = False
        user.save(update_fields=["is_active"])
        inactive_response = self.client.post(
            self.login_url,
            {
                "email": "candidate@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
        )
        self.assertEqual(
            inactive_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assert_error_response(inactive_response)

    def test_protected_endpoint_requires_a_valid_access_token(self):
        self.assertEqual(
            self.client.get(self.protected_url).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.signup()
        login_response = self.login()
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['data']['access']}"
        )

        self.assertEqual(
            self.client.get(self.protected_url).status_code,
            status.HTTP_200_OK,
        )

    def test_refresh_rotation_and_logout_blacklist_refresh_tokens(self):
        self.signup()
        login_response = self.login()
        refresh_token = login_response.data["data"]["refresh"]

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assert_success_response(refresh_response)
        self.assertIn("access", refresh_response.data["data"])
        self.assertIn("refresh", refresh_response.data["data"])

        rotated_refresh = refresh_response.data["data"]["refresh"]
        old_refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(
            old_refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        logout_response = self.client.post(
            self.logout_url,
            {"refresh": rotated_refresh},
            format="json",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assert_success_response(logout_response)
        self.assertEqual(logout_response.data["data"], {})
        blacklisted_response = self.client.post(
            self.refresh_url,
            {"refresh": rotated_refresh},
            format="json",
        )
        self.assertEqual(
            blacklisted_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
