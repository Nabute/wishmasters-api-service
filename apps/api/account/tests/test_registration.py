import faker
from django.utils import timezone
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


class RegisterViewSetTest(APITestCase):

    fixtures = ['lookup.json', 'role.json']

    def setUp(self):
        self.register_url = reverse("register-list")
        self.login_url = reverse("login")
        self.deleted_state = DataLookup.objects.get(
            value=AccountStateType.SUSPENDED.value)
        self.active_state = DataLookup.objects.get(
            value=AccountStateType.ACTIVE.value)
        self.admin_role = Role.objects.get(code=RoleCode.ADMIN.value)
        self.user_role = Role.objects.get(code=RoleCode.PLAYER.value)

        # Create a soft-deleted user
        self.deleted_user = User.objects.create_user(
            email=fake.email(),
            password="1234",
            full_name=fake.name(),
            phone_number=fake.phone_number()[:15],
            state=self.deleted_state,
            role=self.user_role,
            deleted_at=timezone.now()
        )

        # Create an active user
        self.active_user = User.objects.create_user(
            email=fake.email(),
            password="1234",
            full_name=fake.name(),
            phone_number=fake.phone_number()[:15],
            role=self.user_role,
            state=self.active_state
        )

    def test_register_success(self):
        """Test successful registration of a new user."""
        email = fake.email()
        name = fake.name()
        password = "pass1234"
        
        response = self.client.post(
            self.login_url,
            {"email": email, "password": password}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(response.data)
        # Now register
        data = {
            "full_name": name,
            "email": email,
            "password": password
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("success", response.data)

        user = User.objects.get(email=email)
        self.assertEqual(user.full_name, name)
        
        # Checking to relogin
        response = self.client.post(
            self.login_url,
            {"email": email, "password": password}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access_token", response.data)

    def test_register_failure_existing_phone(self):
        """Test registration failure if phone number already exists."""
        email = fake.email()
        User.objects.create(email=email, role=self.user_role, state=self.active_state)
        data = {
            "full_name": fake.name(),
            "email": email,
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_attrs = [error.get("detail") for error in response.data.get(
            "errors", [])]
        self.assertIn("user with this email already exists.", error_attrs)

    def test_register_failure_invalid_phone_number(self):
        """Test registration failure with invalid phone number format."""
        data = {
            "full_name": fake.name(),
            "email": "invalid_phone",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Enter a valid email address.",
            response.data.get("errors")[0].get('detail'))

    def test_register_failure_missing_full_name(self):
        """Test registration failure when full_name is missing."""
        email = fake.email()
        data = {
            "email": email,
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_attrs = [error.get("attr") for error in response.data.get(
            "errors", [])]
        self.assertIn("full_name", error_attrs)

    def test_register_failure_missing_phone_number(self):
        """Test registration failure when phone_number is missing."""
        data = {
            "full_name": fake.name(),
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This field is required.",
            response.data.get("errors")[0].get('detail'))
        self.assertIn(
            "email",
            response.data.get("errors")[0].get('attr'))
