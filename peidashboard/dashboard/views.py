from django.shortcuts import render, redirect
# from django.http import HttpResponseRedirect

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions

from .serializers import SpaceSerializer, AgentGroupSerializer, AgentSerializer, AgentUpdateSerializer, UserSerializer, GroupSerializer, DocumentSerializer, CropSerializer
from .forms import UploadFileForm
from .models import Space, AgentGroup, Agent, AgentUpdate, Document, Crop


# from django.http import HttpResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.parsers import JSONParser

from .models import Snippet
from .serializers import SnippetSerializer

from rest_framework.decorators import api_view

from django.http import Http404
# from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import status

# from rest_framework import mixins
# from rest_framework import generics

from .serializers import UserSerializer

from .permissions import IsOwnerOrReadOnly

from rest_framework.reverse import reverse

from rest_framework import renderers

from rest_framework import viewsets

from rest_framework.decorators import action

import os

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse

import sys

from django.conf import settings

from django.contrib.sites.shortcuts import get_current_site

# Create your views here.
# https://github.com/axelpale/minimal-django-file-upload-example/blob/master/src/for_django_3-0/myapp/views.py
# https://www.django-rest-framework.org/tutorial/quickstart/#serializers
# https://www.django-rest-framework.org/tutorial/
# https://joel-hanson.medium.com/drf-how-to-make-a-simple-file-upload-api-using-viewsets-1b1e65ed65ca


@api_view(['GET'])
def api_root(request, format=None):
	return Response({
		#'users': reverse('user-list', request=request, format=format),
		#'snippets': reverse('snippet-list', request=request, format=format),
		'documents': reverse('document-list', request=request, format=format)
	})

class SpaceViewSet(viewsets.ModelViewSet):
	queryset = Space.objects.all()
	serializer_class = SpaceSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

	def perform_create(self, serializer):
		serializer.save()
	
	def perform_destroy(self, instance):
		return super().perform_destroy(instance)

class AgentGroupViewSet(viewsets.ModelViewSet):
	queryset = AgentGroup.objects.all()
	serializer_class = AgentGroupSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

	def perform_create(self, serializer):
		serializer.save()

class AgentViewSet(viewsets.ModelViewSet):
	queryset = Agent.objects.all()
	serializer_class = AgentSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

	def perform_create(self, serializer):
		serializer.save()

class AgentUpdateViewSet(viewsets.ModelViewSet):
	queryset = AgentUpdate.objects.all()
	serializer_class = AgentUpdateSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

	def perform_create(self, serializer):
		serializer.save()

class CropViewSet(viewsets.ModelViewSet):
	queryset = Crop.objects.all()
	serializer_class = CropSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

	def perform_create(self, serializer):
		serializer.save()

class DocumentViewSet(viewsets.ModelViewSet):
	queryset = Document.objects.all()
	serializer_class = DocumentSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

	def perform_create(self, serializer):
		serializer.save()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	This viewset automatically provides `list` and `retrieve` actions.
	"""
	queryset = User.objects.all()
	serializer_class = UserSerializer


class SnippetViewSet(viewsets.ModelViewSet):
	"""
	This viewset automatically provides `list`, `create`, `retrieve`,
	`update` and `destroy` actions.

	Additionally we also provide an extra `highlight` action.
	"""
	queryset = Snippet.objects.all()
	serializer_class = SnippetSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly,
						  IsOwnerOrReadOnly]

	@action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
	def highlight(self, request, *args, **kwargs):
		snippet = self.get_object()
		return Response(snippet.highlighted)

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class GroupViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows groups to be viewed or edited.
	"""
	queryset = Group.objects.all()
	serializer_class = GroupSerializer
	permission_classes = [permissions.IsAuthenticated]

#@login_required
def index(request):
	if request.user.is_authenticated:
		form = UploadFileForm()
		if request.method == 'POST':
			if 'file_upload' in request.POST:
				form = UploadFileForm(request.POST, request.FILES)
				# Document.objects.all().delete()
				if form.is_valid():
					for f in request.FILES.getlist('docfile'):
						#newdoc = Document(docfile=request.FILES['docfile'])
						newdoc = Document(docfile=f, title=request.POST['title'])
						newdoc.save()
					return redirect('index')
			elif 'doc_delete' in request.POST:
				doc = Document.objects.get(id=int(request.POST['doc_pk']))
				filename = os.path.dirname(os.path.abspath(__file__))+'/../media_cdn/'+str(doc.docfile)
				#print("Deleting", 'media_cdn/'+str(doc.docfile))
				#os.remove('/media_cdn/'+str(doc.docfile))
				#print("Deleting", filename)
				os.remove(filename)
				doc.delete()
			elif 'doc_download' in request.POST:
				return serve_file(request, {})

		documents = Document.objects.all()

		context = {'documents': documents, 'form': form}

		return render(request, 'index.html', context)
	return redirect('/api-auth/login/?next=/')

#@login_required
def file_view(request, slug):
	return serve_file(request, {}, slug)

#@login_required
def serve_file(request, context, slug=''):
	#if request.user.is_authenticated:
	#print(request)
	#print(request.POST)
	if request.POST and 'doc_pk' in request.POST:
		print('DOWNLOAD BUTTON')
		doc = Document.objects.get(id=int(request.POST['doc_pk']))
	else:
		#print('DOWNLOAD URL')
		#print('AAAA', slug)
		doc = Document.objects.get(docfile= ('media/'+slug) )
		#print('DOC', doc)
	filename = "/var/www/myfile.xyz"
	filename = settings.MEDIA_ROOT +'/'+ doc.docfile.name
	#print('OLEOLE', filename)
	response = HttpResponse(content_type='application/force-download')
	downloadname = filename.split('/')[-1]
	response['Content-Disposition']='attachment;filename="%s"'%downloadname
	response["X-Sendfile"] = filename
	response['Content-length'] = os.path.getsize(filename)
	#print(os.path.getsize(filename))
	return response
	#return redirect('index')
	#pass
