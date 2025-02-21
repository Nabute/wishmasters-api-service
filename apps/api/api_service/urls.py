from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static

urlpatterns = i18n_patterns(
    path(f"{settings.ADMIN_URL}", admin.site.urls),
    path("api/", include("api.urls")),
    prefix_default_language=False
)

# Swagger API documentation (optional)
if settings.SHOW_SWAGGER:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

    urlpatterns += [
        path("api/schema", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
