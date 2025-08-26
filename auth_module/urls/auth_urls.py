# auth_module/url/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from auth_module.views.auth_views import AuthViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]
