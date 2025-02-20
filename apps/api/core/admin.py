from decouple import config
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.models import DataLookup, SystemSetting


class BaseModelAdmin(admin.ModelAdmin):
    """
    Abstract admin class
    """

    # Use the global_objects manager for admin queryset
    def get_queryset(self, request):
        """
        Override get_queryset to include all records,
        including soft-deleted ones.
        """
        if hasattr(self.model, "global_objects"):
            return self.model.global_objects.all()
        return super().get_queryset(request)


admin.site.register(SystemSetting, BaseModelAdmin)


@admin.register(DataLookup)
class DataLookupAdmin(BaseModelAdmin):

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "type",
                    "name",
                    "value",
                    "category",
                    "is_default",
                    "note",
                    "index",
                ),
            },
        ),
    )

    fieldsets = (
        (None, {"fields": (
            "type",
            "name",
            "description",
            "value",
            "category",
            "is_default",
            "note",
            "index",
        )}),

        (
            _("Actions"),
            {"classes": ("collapse",),
             "fields": ("is_active", "remark",), },
        ),
    )

    list_display = (
        "type",
        "name",
        "value",
        "category",
        "is_active",
        "is_default",
        "index",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "updated_at",
        "type",
        "category",
    )


admin.site.site_title = _(config("APP_TITLE", cast=str))
admin.site.site_header = _(config("APP_TITLE", cast=str))
admin.site.index_title = _(config("INDEX_TITLE", cast=str))
