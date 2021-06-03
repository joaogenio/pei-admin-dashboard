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
router.register(r'agentupdates', views.AgentUpdateViewSet)
router.register(r'agent', views.AgentViewSet)
router.register(r'agentgroups', views.AgentGroupViewSet)
router.register(r'spaces', views.SpaceViewSet)
router.register(r'people', views.PersonViewSet)
router.register(r'stats', views.StatsViewSet)
router.register(r'contentprograms', views.ContentProgramViewSet)
router.register(r'programentries', views.ProgramEntryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name='index'),
    
    path('api-auth/', include('rest_framework.urls'), name='api-auth'),

    path('api/', include(router.urls), name='api'),

    path('download/<slug>', views.file_view, name='file_view'),

    path('control/<int:id>', views.control_view, name='control_view'),

    path('spaces/', views.space_view, name='space_view'),
    path('spaces/addgroup/<int:space>', views.space_create_group, name='space_create_group'),
    #path('spaces/<int:id>', views.space_individual, name='space_individual'),

    #path('groups/', views.group_view, name='group_view'),
    path('groups/<int:id>', views.group_individual, name='group_individual'),

    path('agents/', views.agent_view, name='agent_view'),
    #path('agents/<int:id>', views.agent_individual, name='agent_individual'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
