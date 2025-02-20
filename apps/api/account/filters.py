from django_filters import FilterSet
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model


class UserFilter(FilterSet):
    status = filters.UUIDFilter(
        field_name='status',
        lookup_expr='exact')

    association = filters.UUIDFilter(
        field_name='parking_association_member__association',
        lookup_expr='exact')

    financial_institution = filters.UUIDFilter(
        field_name='employee__institution',
        lookup_expr='exact')

    clearance_institution = filters.UUIDFilter(
        field_name='clearance_institution_employee__institution',
        lookup_expr='exact')

    role = filters.UUIDFilter(field_name='role',
                              lookup_expr='exact')

    class Meta:
        model = get_user_model()
        fields = []
