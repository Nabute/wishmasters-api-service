# from django.urls import reverse
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from account.models import User, Role

from account.forms import UserCreationForm, UserChangeForm
from core.models import DataLookup
from core.admin import BaseModelAdmin


class UserAdmin(BaseUserAdmin, BaseModelAdmin):
    # The forms to add and change user instances
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ['full_name', 'email', 'phone_number', 'is_admin', 'role']
    list_filter = ['is_admin', 'role']
    fieldsets = [
        (None, {'fields': ['email', 'phone_number', 'password']}),
        ("Personal info", {"fields": ['full_name']}),
        ('Permissions', {'fields': ['is_active', 'is_admin', 'state', 'role']}),
        ('Important dates', {'fields': ['created_at', 'updated_at',
                                        'deleted_at']})
    ]

    add_fieldsets = [
        (None, {
            'classes': ['wide'],
            'fields': ['full_name', 'email', 'phone_number', 'password1',
                       'password2', 'is_active', 'is_admin',
                       'state', 'role']})
    ]

    search_fields = ['full_name', 'email', 'phone_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = []


@admin.register(Role)
class RoleAdmin(BaseModelAdmin):
    list_display = ('name', 'code')
    list_filter = ('parents',)
    search_fields = ('name', 'code')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('children')


admin.site.register(User, UserAdmin)

admin.site.unregister(Group)