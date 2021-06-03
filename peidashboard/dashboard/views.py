from django.shortcuts import render, redirect
# from django.http import HttpResponseRedirect

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions

from .serializers import *
from .forms import *
from .models import *

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

from django.shortcuts import get_object_or_404

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

class ContentProgramViewSet(viewsets.ModelViewSet):
	queryset = ContentProgram.objects.all()
	serializer_class = ContentProgramSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProgramEntryViewSet(viewsets.ModelViewSet):
	queryset = ProgramEntry.objects.all()
	serializer_class = ProgramEntrySerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AgentUpdateViewSet(viewsets.ModelViewSet):
	queryset = AgentUpdate.objects.all()
	serializer_class = AgentUpdateSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PersonViewSet(viewsets.ModelViewSet):
	queryset = Person.objects.all()
	serializer_class = PersonSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class StatsViewSet(viewsets.ModelViewSet):
	queryset = Stats.objects.all()
	serializer_class = StatsSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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

				###   FILE UPLOAD   ###
				print("request.FILES.getlist('docfile')", request.FILES.getlist('docfile'))
				if request.FILES.getlist('docfile') != []:
					print("ISSA FILE")
					form = UploadFileForm(request.POST, request.FILES)
					# Document.objects.all().delete()
					if form.is_valid():
						for f in request.FILES.getlist('docfile'):
							newdoc = Document(docfile=f, title=request.POST['title'])
							newdoc.save()
						return redirect('index')

				###   YOUTUBE LINK UPLOAD   ###

				else:
					form = UploadFileForm(request.POST)
					if form.is_valid():
						newdoc = Document(youtubelink=request.POST['youtubelink'], title=request.POST['title'])
						newdoc.save()
						return redirect('index')

			###   DELETE FILE   ###

			elif 'doc_delete' in request.POST:
				doc = Document.objects.get(id=int(request.POST['doc_pk']))
				filename = os.path.dirname(os.path.abspath(__file__))+'/../media_cdn/'+str(doc.docfile)
				#print("Deleting", 'media_cdn/'+str(doc.docfile))
				#print("Deleting", filename)
				os.remove(filename)
				doc.delete()
			elif 'doc_download' in request.POST:
				return serve_file(request, {})
			
			###   DELETE LINK   ###

			elif 'link_delete' in request.POST:
				doc = Document.objects.get(id=int(request.POST['doc_pk']))
				doc.delete()

		###   VIEW HANDLING   ###

		#html = dir_tree_builder(os.path.dirname(os.path.abspath(__file__))+'/../media_cdn/media/')

		documents = Document.objects.all()

		context = {'documents': documents, 'form': form}

		return render(request, 'index.html', context)
	return redirect('/api-auth/login/?next=/')

def dir_tree_builder(dir):
	print(sorted(list(os.listdir(dir))))
	for file in sorted(list(os.listdir(dir))):
		print(file, "dir?", os.path.isdir(dir+file))

def group_individual(request, id):
	if request.user.is_authenticated:
		programform = ContentProgramForm()
		entryform = ProgramEntryForm()
		if request.method == 'POST':
			if 'program_upload' in request.POST:
				programform = ContentProgramForm(request.POST)
				if programform.is_valid():
					group = programform.cleaned_data['group']
					name = programform.cleaned_data['name']
					start_date = programform.cleaned_data['start_date']
					program = ContentProgram(group=group, name=name, start_date=start_date)
					program.save()
			elif 'entry_upload' in request.POST:
				entryform = ProgramEntryForm(request.POST)
				if entryform.is_valid():
					program = entryform.cleaned_data['program']
					doc = entryform.cleaned_data['doc']
					duration = entryform.cleaned_data['duration']
					entry = ProgramEntry(program=program, doc=doc, duration=duration)
					entry.save()
			elif 'program_delete' in request.POST:
				programid = request.POST['program']
				program = ContentProgram.objects.get(pk=programid)
				program.delete()
			elif 'entry_delete' in request.POST:
				entryid = request.POST['entry']
				entry = ProgramEntry.objects.get(pk=entryid)
				entry.delete()
			return redirect('group_individual', id)
		entries = ProgramEntry.objects.all()
		group = get_object_or_404(AgentGroup, pk=id)
		documents = Document.objects.all()
		context = {'entries': entries, 'documents': documents, 'group': group, 'programform': programform, 'entryform': entryform}
		return render(request, "group_individual.html", context)
	return redirect('/api-auth/login/?next=/spaces')

def agent_view(request):
	if request.user.is_authenticated:
		form = AgentForm()
		if request.method == 'POST':

			###   AGENT UPLOAD   ###

			if 'agent_upload' in request.POST:
				form = AgentForm(request.POST)
				print(request.POST)
				if form.is_valid():
					id = form.cleaned_data['id']
					name = form.cleaned_data['name']
					group = form.cleaned_data['group']
					print(id,name,group)
					agent = Agent(id=id, name=name, group=group)
					print(agent)
					agent.save()
					return redirect('agent_view')

			###   DELETE AGENT   ###

			elif 'agent_delete' in request.POST:
				agent = Agent.objects.get(id=int(request.POST['agent_pk']))
				agent.delete()

		###   VIEW HANDLING   ###

		agents = Agent.objects.all()
		groups = AgentGroup.objects.all()

		context = {'agents': agents, 'groups': groups, 'form': form}

		return render(request, 'agent_view.html', context)
	return redirect('/api-auth/login/?next=/agents')

def space_view(request):
	if request.user.is_authenticated:
		spaceform = SpaceForm()
		groupform = AgentGroupForm()
		if request.method == 'POST':
			if 'space_submit' in request.POST:
				spaceform = SpaceForm(request.POST)
				if spaceform.is_valid():
					name = spaceform.cleaned_data['name']
					space = Space(name=name)
					space.save()
					return redirect('space_view')
			#elif 'group_submit' in request.POST:
			#	groupform = AgentGroupForm(request.POST)
			#	if groupform.is_valid():
			#		name = groupform.cleaned_data['name']
			#		space = groupform.cleaned_data['space']
			#		group = AgentGroup(name=name, space=space)
			#		group.save()
			#		return redirect('space_view')
		agents = Agent.objects.all()
		groups = AgentGroup.objects.all()
		spaces = Space.objects.all()
		context = {'spaces': spaces, 'groups': groups, 'agents': agents,
			'spaceform': spaceform, 'groupform': groupform}
		return render(request, 'space_view.html', context)
	return redirect('/api-auth/login/?next=/spaces')

def space_create_group(request, space):
	if request.user.is_authenticated:
		if request.method == 'POST':
			if 'group_submit' in request.POST:
				groupform = AgentGroupForm(request.POST)
				if groupform.is_valid():
					name = groupform.cleaned_data['name']
					space = Space.objects.get(pk=space)
					group = AgentGroup(name=name, space=space)
					group.save()
					return redirect('space_view')
				else:
					# como reportar erros?? :S
					return redirect('space_view')
		else:
			return redirect('/spaces')
	return redirect('/api-auth/login/?next=/spaces')

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

def control_view(request, id):
	if request.method == 'POST':
		print(id)
		doc_pk = request.POST['doc_pk']
		print(doc_pk)

		update = AgentUpdate.objects.get(agent=id)
		update.contentid = Document.objects.get(pk=doc_pk)
		update.content_confirm = False
		update.save()

	agent = Agent.objects.get(pk=id)
	documents = Document.objects.all()
	context = {'documents': documents, 'agent': agent}
	return render(request, 'control.html', context)