"""
URL configuration for camerasDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from myapp import views
from two_factor.urls import urlpatterns as two_factor_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('monitoreo/', views.monitoreo, name='monitoreo'),
    path('log-error/', views.log_error, name='log_error'),
    path('load_camera_iframe/', views.load_camera_iframe, name='load_camera_iframe'),
    path('', (two_factor_urls,'two_factor','two_factor')),  # URLs de django-two-factor-auth
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
