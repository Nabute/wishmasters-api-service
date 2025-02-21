from django.utils.translation import gettext as _
from account.enums import RoleCode
from core.validators import validate_email
from core.models import DataLookup
from core.serializers import DataLookupSerializer
from core.enums import AccountStateType
from rest_framework import serializers
from django.db import transaction
from django.utils.crypto import constant_time_compare
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken

from account.models import Role

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'full_name', 'email', 'phone_number',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'created_at', 'updated_at']


class AllUserSerializer(serializers.ModelSerializer):
    role = RoleSerializer()
    state = DataLookupSerializer()

    class Meta:
        model = UserModel
        fields = ['id', 'full_name', 'email', 'phone_number', 'role',
                  'state', 'created_at', 'updated_at']


class ProfileSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = UserModel
        fields = ['id', 'full_name', 'email', 'phone_number',
                  'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'email',
                            'created_at', 'updated_at']

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.full_name = validated_data.get('full_name', instance.full_name)
            instance.phone_number = validated_data.get('phone_number', instance.phone_number)
            instance.save()
            return instance


class AccountStateSerializer(serializers.ModelSerializer):

    state = serializers.PrimaryKeyRelatedField(
        queryset=DataLookup.objects.filter(
            type=AccountStateType.TYPE.value), required=True)

    class Meta:
        model = UserModel
        fields = ['id', 'state',]

    def to_representation(self, instance):
        return ProfileSerializer(
            instance).to_representation(instance)

    def update(self, instance, validated_data):
        """Update user state with validated state data."""
        state = validated_data.get('state')
        instance.update_state_to(state)
        return instance


class LoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=256)
    refresh_token = serializers.CharField(max_length=256)


class RegisterResponseSerializer(serializers.Serializer):
    success = serializers.CharField(max_length=256)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'full_name', 'email']

    def create(self, validated_data):
        with transaction.atomic():
            validated_data['role'] = Role.objects.get(code=RoleCode.PLAYER.value)
            validated_data['state'] = DataLookup.objects.get(
                value=AccountStateType.ACTIVE.value)

            return UserModel.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        """Validate email, password, and account state."""
        email = attrs.get('email')
        password = attrs.get('password')

        user = UserModel.objects.filter(email=email).first()

        # Create a dummy user instance for consistent password hashing time
        dummy_password = UserModel().password

        if not user:
            # Use constant_time_compare with dummy_password for a
            # consistent response time
            constant_time_compare(dummy_password, password)
            raise serializers.ValidationError(_("Invalid email or password"))

        # Django's check_password already uses constant time
        # comparison internally
        if not user.check_password(password):
            raise serializers.ValidationError(_("Invalid email or password"))

        if user.state.value != AccountStateType.ACTIVE.value:
            raise serializers.ValidationError(_("Account is not active"))

        return attrs

class TokenRefreshSerializer(serializers.Serializer):
    refreshToken = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs):
        refreshToken = self.token_class(attrs["refreshToken"])

        data = {"access_token": str(refreshToken.access_token)}

        api_settings = getattr(settings, "SIMPLE_JWT", None)

        if api_settings["ROTATE_REFRESH_TOKENS"]:
            refreshToken.set_jti()
            refreshToken.set_exp()
            refreshToken.set_iat()

            data["refresh_token"] = str(refreshToken)

        return data

