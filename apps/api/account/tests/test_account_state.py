import faker
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import DataLookup
from core.enums import AccountStateType

from account.enums import RoleCode
from account.models import Role

User = get_user_model()
fake = faker.Faker()


class AccountStateViewTest(APITestCase):

    fixtures = ['lookup.json', 'role.json']

    def setUp(self):
        self.account_state_url = reverse("account-state-detail", args=[1])
        self.state_active = DataLookup.objects.get(
            value=AccountStateType.ACTIVE.value,
        )
        self.state_inactive = DataLookup.objects.get(
            value=AccountStateType.SUSPENDED.value,
        )

        # Set up roles
        self.admin_role = Role.objects.get(
            code=RoleCode.ADMIN.value
        )
        self.user_role = Role.objects.get(
            code=RoleCode.USER.value
        )

        # Admin user
        self.admin_user = User.objects.create_user(
            email=fake.email(),
            password="1234",
            full_name=fake.name(),
            phone_number=fake.phone_number()[:15],
            role=self.admin_role,
            state=self.state_active
        )

        # Regular user
        self.regular_user = User.objects.create_user(
            email=fake.email(),
            password="1234",
            full_name=fake.name(),
            phone_number=fake.phone_number()[:15],
            role=self.user_role,
            state=self.state_active
        )

    def test_admin_can_update_user_state(self):
        """Admin should be able to update the state of any user."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("account-state-detail", args=[self.regular_user.id])
        payload = {"state": str(self.state_inactive.id)}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.state, self.state_inactive)

    def test_user_cannot_update_own_state(self):
        """Regular user should not be able to update their own state."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(self.account_state_url, {
            "user": self.regular_user.id,
            "state": self.state_inactive.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_update_other_user_state(self):
        """Regular user should not be able to update any state."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(self.account_state_url, {
            "user": self.admin_user.id,
            "state": self.state_inactive.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_state_invalid_user(self):
        """Test updating with an invalid user ID."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.account_state_url, {
            "user": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "state": self.state_inactive.id
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            "Not found.",
            response.data.get('errors')[0]['detail'])

    def test_update_state_invalid_state(self):
        """Test updating with an invalid state ID."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.account_state_url, {
            "user": self.regular_user.id,
            "state": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            "Not found.",
            response.data.get('errors')[0]['detail'])

    def test_unauthenticated_user_access(self):
        """Ensure unauthenticated users cannot update states."""
        response = self.client.patch(self.account_state_url, {
            "user": self.regular_user.id,
            "state": self.state_inactive.id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
