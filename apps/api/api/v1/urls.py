from django.urls import include, path

urlpatterns = [
    path("core/", include("core.urls")),
    path("account/", include("account.urls")),
    path("games/", include("games.urls")),
]
