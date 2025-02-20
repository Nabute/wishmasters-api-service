from django.db import models
from django.utils.translation import gettext_lazy as _
from core.abstract import AbstractBaseModel


class DataLookup(AbstractBaseModel):

    type = models.CharField(
        max_length=256,
        verbose_name=_("type")
    )

    name = models.CharField(
        max_length=256,
        verbose_name=_("name")
    )

    value = models.CharField(
        max_length=256,
        verbose_name=_("value")
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("description")
    )

    category = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name=_("category")
    )

    note = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("note")
    )

    index = models.PositiveIntegerField(
        default=0,
        verbose_name=_("index")
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name=_("is default")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active")
    )

    remark = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("remark"),
    )

    class Meta:
        verbose_name = _("data lookup")
        verbose_name_plural = _("data lookups")
        db_table = "data_lookups"
        constraints = [
            # Constraint: Only one default value per type
            models.UniqueConstraint(
                fields=["type", "is_default"],
                condition=models.Q(is_default=True),
                name="data_lookups_type_is_default_idx"
            ),

            # Constraint: Unique index for each type
            models.UniqueConstraint(
                fields=["type", "index"],
                name="data_lookups_type_index_idx"
            ),

            # Constraint: Unique value across all types
            models.UniqueConstraint(
                fields=["value"],
                name="data_lookups_value_idx"
            ),
        ]

    def __str__(self):
        return f"{self.type} :: {self.name}"


class SystemSetting(AbstractBaseModel):

    name = models.CharField(
        max_length=256,
        verbose_name=_("name")
    )

    key = models.CharField(
        max_length=256,
        verbose_name=_("key")
    )

    default_value = models.CharField(
        max_length=256,
        verbose_name=_("default_value")
    )

    current_value = models.CharField(
        max_length=256,
        verbose_name=_("current_value")
    )

    data_scheme = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("data_scheme")
    )

    class Meta:
        verbose_name = _("system setting")
        verbose_name_plural = _("system settings")
        db_table = "system_settings"
        constraints = [
            # Constraint: Unique key
            models.UniqueConstraint(
                fields=["key"],
                name="system_settings_key_idx"
            ),
        ]

    def __str__(self):
        return f"{self.key} :: {self.current_value}"
