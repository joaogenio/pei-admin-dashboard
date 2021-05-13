"""peidashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from dashboard import views

#from django.views.generic import RedirectView
from django.urls import include, path
from rest_framework import routers

#from rest_framework.urlpatterns import format_suffix_patterns

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
#router.register(r'snippets', views.SnippetViewSet)
#router.register(r'users', views.UserViewSet)
router.register(r'documents', views.DocumentViewSet)
router.register(r'crops', views.CropViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name='index'),
    
    path('api-auth/', include('rest_framework.urls'), name='api-auth'),

    path('api/', include(router.urls), name='api'),

    path('download/<slug>', views.file_view, name='file_view')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
