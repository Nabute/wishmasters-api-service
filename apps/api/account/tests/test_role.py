import faker
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from account.models import Role
from account.enums import RoleCode
from core.models import DataLookup
from core.enums import AccountStateType


User = get_user_model()
fake = faker.Faker()


class RoleAccessPolicyTestCase(TestCase):
    fixtures = ['lookup.json', 'role.json']

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('roles-list')

        self.active_state = DataLookup.objects.get(
            value=AccountStateType.ACTIVE.value)

        self.admin_role = Role.objects.get(
            code=RoleCode.ADMIN.value)
        self.user_role = Role.objects.get(code=RoleCode.USER.value)

        self.admin_user = User.objects.create_user(
            email=fake.email(),
            password="adminpass",
            role=self.admin_role,
            state=self.active_state,
            phone_number=fake.phone_number()[:15]
        )
        self.user_role_user = User.objects.create_user(
            email=fake.email(),
            password="userpass",
            role=self.user_role,
            state=self.active_state,
            phone_number=fake.phone_number()[:15],
        )

    def test_admin_access(self):
        """Admin should see all roles."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_roles = [role.value for role in RoleCode]
        response_role_names = [
            role['code'] for role in response.data]
        self.assertCountEqual(response_role_names, expected_roles)

    def test_user_access(self):
        """User role should only see itself."""
        self.client.force_authenticate(user=self.user_role_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User can only see itself
        expected_roles = [RoleCode.USER.value]
        response_role_codes = [role['code'] for role in response.data]
        self.assertCountEqual(response_role_codes, expected_roles)
