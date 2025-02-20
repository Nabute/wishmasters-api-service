import faker
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import DataLookup
from core.enums import AccountStateType
from account.models import Role
from account.enums import RoleCode

User = get_user_model()
fake = faker.Faker()


class LoginViewTest(APITestCase):
    fixtures = ['lookup.json', 'role.json']

    def setUp(self):
        self.email_login_url = reverse("login")
        self.valid_email = fake.email()
        self.valid_password = "password123"
        self.invalid_email = "invalid_email@example.com"
        self.invalid_password = "wrongpassword"

        self.deleted_state = DataLookup.objects.get(
            value=AccountStateType.SUSPENDED.value)
        self.active_state = DataLookup.objects.get(
            value=AccountStateType.ACTIVE.value)
        self.admin_role = Role.objects.get(code=RoleCode.ADMIN.value)
        self.user_role = Role.objects.get(code=RoleCode.USER.value)

        # Create active user with valid credentials
        self.user = User.objects.create_user(
            email=self.valid_email,
            password=self.valid_password,
            full_name=fake.name(),
            state=self.active_state,
            role=self.user_role
        )

        # Create inactive user
        self.inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password="password123",
            full_name=fake.name(),
            state=self.deleted_state,
            role=self.user_role
        )

    def test_email_login_success(self):
        """Test login with valid credentials for an active user."""
        response = self.client.post(
            self.email_login_url,
            {"email": self.valid_email, "password": self.valid_password}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access_token", response.data)

    def test_email_login_failure_invalid_credentials(self):
        """Test login with invalid email and/or password."""
        response = self.client.post(
            self.email_login_url,
            {"email": self.valid_email, "password": self.invalid_password}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors')[0]['detail'],
            "Invalid email or password",
        )

        response = self.client.post(
            self.email_login_url,
            {"email": self.invalid_email, "password": self.valid_password}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors')[0]['detail'],
            "Invalid email or password",
        )

    def test_email_login_failure_inactive_account(self):
        """Test login with a valid user who is inactive."""
        response = self.client.post(
            self.email_login_url,
            {"email": "inactive@example.com", "password": "password123"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors')[0]['detail'],
            'Account is not active',
        )

    def test_email_login_failure_invalid_email_format(self):
        """Test login with an invalid email format."""
        response = self.client.post(
            self.email_login_url,
            {"email": "invalid-email-format", "password": self.valid_password}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors')[0]['detail'],
            'Enter a valid email address.'
        )

    def test_email_login_missing_fields(self):
        """Test login with missing email or password fields."""
        response = self.client.post(
            self.email_login_url, {"email": self.valid_email})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors')[0]['detail'],
            'This field is required.'
        )

        response = self.client.post(
            self.email_login_url, {"password": self.valid_password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors')[0]['detail'],
            'This field is required.'
        )
