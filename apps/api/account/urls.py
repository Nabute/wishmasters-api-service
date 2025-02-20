from django.urls import path
from account.views import (
    AccountStateView, EmailLoginView, ProfileView,
    RegisterViewSet, RoleViewSet, TokenRefreshView,
    UserViewSet)
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register('roles', RoleViewSet, basename='roles')
router.register('users', UserViewSet, basename="users")
router.register('register', RegisterViewSet,
                basename='register')
router.register('state', AccountStateView,
                basename='account-state')


urlpatterns = router.urls + [
    path('login', EmailLoginView.as_view(), name='login'),
    path('refresh-token', TokenRefreshView.as_view(), name='refresh-token'),
    path('profile', ProfileView.as_view(), name='profile'),   
]