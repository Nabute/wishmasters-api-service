import faker
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import DataLookup
from core.enums import AccountStateType

from account.enums import RoleCode
from account.models import Role


User = get_user_model()
fake = faker.Faker()


class ProfileViewTest(APITestCase):

    fixtures = ['lookup.json', 'role.json']

    def setUp(self):
        self.profile_url = reverse("profile")
        self.active_state = DataLookup.objects.get(
            value=AccountStateType.ACTIVE.value)
        self.user_role = Role.objects.get(code=RoleCode.PLAYER.value)
        self.email = fake.email()
        self.name = fake.name()
        self.user = User.objects.create_user(
            email=self.email,
            password="1234",
            full_name=self.name,
            phone_number=fake.phone_number()[:15],
            role=self.user_role,
            state=self.active_state
        )
        self.client.force_authenticate(user=self.user)

    def test_profile_view_success(self):
        """Test successful retrieval of the profile data."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.email)
        self.assertEqual(response.data["full_name"], self.name)

    def test_profile_update_success(self):
        """Test successful update of the profile with valid data."""
        data = {"full_name": "John Updated"}
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], "John Updated")

    def test_profile_update_failure_missing_required_field(self):
        """Test update failure due to missing required fields."""
        data = {"full_name": ""}
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors')[0],
            {
                'code': 'blank',
                'detail': 'This field may not be blank.',
                'attr': 'full_name'
            },
        )

    def test_profile_update_partial_without_preferences(self):
        """Test partial update without changing preferences."""
        data = {"full_name": "John Partial Update"}
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], "John Partial Update")
        self.assertEqual(response.data["email"], self.email)
