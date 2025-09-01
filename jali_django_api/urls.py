"""
URL configuration for jali_django_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('auth_module.urls.auth_urls')),  # Auth module URLs
    path('api/',include('hospital_module.urls')),  # Hospital module URLs
    path('api/',include('cards_module.urls')),  # Cards module URLs
    path('api/',include('medical_module.urls')),  # Medical module URLs
    path('api/',include('patiente__module.urls')),  # Patiente module URLs
    
]
