from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import HopitalViewSet

router = DefaultRouter()
router.register(r'hospitals', HopitalViewSet, basename='hospital')

urlpatterns = [
    path('', include(router.urls)),
]
