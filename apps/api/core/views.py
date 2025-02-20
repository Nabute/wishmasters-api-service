from rest_framework import (viewsets, mixins)
from rest_framework.permissions import AllowAny
from rest_framework import filters
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from http import HTTPMethod

from django_filters.rest_framework import DjangoFilterBackend

from .models import DataLookup, SystemSetting
from .serializers import (DataLookupSerializer,
                          DataLookupTypeSerializer,
                          SystemSettingSerializer,
                          ResetSystemSettingSerializer,
                          SystemSettingResponseSerializer)


class DataLookupViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    pagination_class = None
    queryset = DataLookup.objects.all()
    serializer_class = DataLookupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['type', 'name', 'value', 'category',
                     "is_default", 'is_active']
    filterset_fields = ['type', 'value', 'category',
                        "is_default", 'is_active']


class DataLookupTypeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    pagination_class = None
    queryset = DataLookup.objects.all().distinct('type').order_by('type')
    serializer_class = DataLookupTypeSerializer


@extend_schema(
    responses=SystemSettingResponseSerializer
)
class SystemSettingViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = SystemSetting.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = SystemSettingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    @extend_schema(
        responses=SystemSettingResponseSerializer
    )
    @action(url_path='reset',
            detail=True,
            methods=[HTTPMethod.PATCH],
            serializer_class=ResetSystemSettingSerializer
            )
    def reset(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, instance=instance)
        if serializer.is_valid(raise_exception=True):
            instance.current_value = instance.default_value
            instance.save()
            return Response(SystemSettingResponseSerializer(
                instance).data, status=status.HTTP_200_OK)
