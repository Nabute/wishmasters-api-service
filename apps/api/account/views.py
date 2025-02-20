from account.serializers import (
    AccountStateSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
    RoleSerializer,
    AllUserSerializer)

from account.permissions import (
    AccountStateAccessPolicy, RoleAccessPolicy, UserAccessPolicy)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import (
    TokenRefreshView as BaseTokenRefreshView)
from rest_framework_simplejwt.tokens import RefreshToken
from account.enums import RoleCode

from .filters import UserFilter

from rest_framework import status
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, mixins
from account.models import Role
from core.decorators import swagger_safe


UserModel = get_user_model()


class RoleViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, RoleAccessPolicy]
    queryset = Role.objects.all()
    pagination_class = None
    serializer_class = RoleSerializer

    @property
    def access_policy(self):
        return self.permission_classes[1]

    @swagger_safe(Role)
    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, Role.objects.all()
        )


class UserViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated, UserAccessPolicy]
    serializer_class = AllUserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserFilter
    search_fields = ['full_name']

    @property
    def access_policy(self):
        return self.permission_classes[1]

    @swagger_safe(get_user_model())
    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, get_user_model().objects.all()
        )


@extend_schema(
    responses=LoginResponseSerializer
)
class EmailLoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = UserModel.objects.get(
            email=serializer.validated_data['email'])
        token = RefreshToken.for_user(user)
        response_data = {
            'refresh_token': str(token),
            'access_token': str(token.access_token),
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    responses=ProfileSerializer
)
class AccountStateView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    http_method_names = ['patch']
    permission_classes = [IsAuthenticated, AccountStateAccessPolicy]
    serializer_class = AccountStateSerializer

    @property
    def access_policy(self):
        return self.permission_classes[1]

    @swagger_safe(UserModel)
    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, UserModel.objects.all()
        )


class TokenRefreshView(BaseTokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response


@extend_schema(
    responses=RegisterSerializer
)
class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    queryset = get_user_model().objects.all()
