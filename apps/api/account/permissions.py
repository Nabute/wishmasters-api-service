from account.models import Role
from account.enums import RoleCode
from django.db.models import Q
from core.permissions import AbstractAccessPolicy


class RoleAccessPolicy(AbstractAccessPolicy):

    @classmethod
    def scope_queryset(cls, request, queryset):
        """
        Restrict the queryset to roles that are:
        - The user's own role
        - Descendant roles of the user's role
        - Roles visible to multiple parent roles (e.g.,
            BranchOffice visible to multiple managers)
        """
        user_role = request.user.role

        if not user_role:
            # No role assigned to the user, return empty
            return queryset.none()

        # Get user role descendants
        descendants = user_role.get_descendants()
        descendant_ids = [role.id for role in descendants]

        # Include the user's role and all descendants
        return queryset.filter(
            Q(id=user_role.id) | Q(id__in=descendant_ids)
        )


class UserAccessPolicy(AbstractAccessPolicy):

    @classmethod
    def scope_queryset(cls, request, queryset):
        user_role = request.user.role
        if user_role.code == RoleCode.ADMIN.value:
            return queryset

        accessible_role_ids = {descendant.id for descendant in user_role.get_descendants()} # noqa
        accessible_role_ids.add(user_role.id)

        # Filter to include only users with roles in accessible_role_ids
        return queryset.filter(role__id__in=accessible_role_ids)


class AccountStateAccessPolicy(AbstractAccessPolicy):
    """
    Policy for updating account states, restricting access to specific roles.
    """

    @classmethod
    def scope_queryset(cls, request, queryset):
        auth_user = request.user

        # Allow admins full access, others can only update their own records
        if auth_user.role.code == RoleCode.ADMIN.value:
            return queryset
        return queryset.none()
