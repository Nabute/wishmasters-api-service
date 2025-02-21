from account.enums import RoleCode
from django.utils.timezone import now
from core.permissions import AbstractAccessPolicy


class CompetitionAccessPolicy(AbstractAccessPolicy):

    @classmethod
    def scope_queryset(cls, request, queryset):
        user_role = request.user.role
        if user_role.code == RoleCode.ADMIN.value:
            return queryset
        # The rest of the users can only see currenly active competitions
        return queryset.filter(start_time__lte=now(), end_time__gte=now())
