from rest_framework import routers
from games.views import CompetitionViewSet

router = routers.DefaultRouter(trailing_slash=False)

router.register('competitions', CompetitionViewSet, basename='competitions')

urlpatterns = router.urls
