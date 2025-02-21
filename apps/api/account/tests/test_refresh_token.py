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


class TokenRefreshViewTest(APITestCase):

    fixtures = ['lookup.json', 'role.json']

    def setUp(self):
        self.active_state = DataLookup.objects.get(
            value=AccountStateType.ACTIVE.value)
        self.admin_role = Role.objects.get(code=RoleCode.ADMIN.value)
        self.user_role = Role.objects.get(code=RoleCode.PLAYER.value)
        self.user = User.objects.create_user(
            email=fake.email(),
            password="1234",
            full_name=fake.name(),
            phone_number=fake.phone_number()[:15],
            role=self.user_role,
            state=self.active_state
        )
        self.token = RefreshToken.for_user(self.user)
        self.refresh_token_url = reverse("refresh-token")

    def test_token_refresh_success(self):
        response = self.client.post(
            self.refresh_token_url, {"refreshToken": str(self.token)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

