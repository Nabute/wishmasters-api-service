from datetime import timedelta
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from account.managers import UserManager

from core.models import DataLookup, SystemSetting
from core.enums import SystemSettingKey
from core.abstract import AbstractBaseModel
from django_softdelete.models import DeletedManager


class Role(AbstractBaseModel):

    name = models.CharField(
        max_length=256,
        verbose_name=_("name")
    )

    code = models.CharField(
        max_length=256,
        verbose_name=_("code")
    )

    parents = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name="children",
        verbose_name=_("parent roles")
    )

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        ordering = ("-created_at",)
        db_table = "roles"
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(deleted_at__isnull=True),
                name="roles_code_idx"
            ),
        ]
        indexes = [
            models.Index(
                fields=["created_at"],
                name="roles_created_at_idx"
            ),
            models.Index(
                fields=["updated_at"],
                name="roles_updated_at_idx"
            ),
            models.Index(
                fields=["deleted_at"],
                name="roles_deleted_at_idx"
            )
        ]

    def __str__(self):
        return self.name

    def get_child_roles(self):
        return self.children.all()

    def get_descendants(self):
        """Recursively fetch all descendants."""
        descendants = set()
        children = self.get_child_roles()
        for child in children:
            descendants.add(child)
        return descendants


class User(AbstractBaseUser, AbstractBaseModel):
    full_name = models.CharField(
        max_length=256,
        verbose_name=_("full name")
    )

    email = models.EmailField(
        unique=True,
        max_length=256,
        verbose_name=_("email")
    )

    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name=_("phone number")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("active")
    )

    is_admin = models.BooleanField(
        default=False,
        verbose_name=_("staff")
    )

    role = models.ForeignKey(
        Role,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="+"
    )

    state = models.ForeignKey(
        DataLookup,
        on_delete=models.RESTRICT,
        blank=True,
        related_name="+",
        limit_choices_to={'type': "account_state"}
    )

    password_reset_code = models.CharField(
        max_length=6,
        null=True,
        blank=True,
        verbose_name=_("password reset code")
    )

    password_reset_code_expiry = models.DateTimeField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_("password reset code")
    )

    objects = UserManager()
    deleted_objects = DeletedManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ("-created_at",)
        db_table = "users"
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(email__isnull=False) & models.Q(deleted_at__isnull=True),
                name="users_email_idx"
            )
        ]
        indexes = [
            models.Index(
                fields=["created_at"],
                name="users_created_at_idx"
            ),
            models.Index(
                fields=["updated_at"],
                name="users_updated_at_idx"
            ),
            models.Index(
                fields=["deleted_at"],
                name="users_deleted_at_idx"
            )
        ]

    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def update_state_to(self, new_state):
        if new_state.value != self.state.value:
            self.state = new_state
            self.save()
