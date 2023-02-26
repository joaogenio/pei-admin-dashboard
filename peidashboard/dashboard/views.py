from datetime import timedelta
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

from rest_framework.decorators import api_view

# from django.http import Http404
# from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import status

# from rest_framework import mixins
# from rest_framework import generics

from .permissions import IsOwnerOrReadOnly

from rest_framework.reverse import reverse

from rest_framework import renderers

from rest_framework import viewsets

from rest_framework.decorators import action

import os

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseNotFound

import sys

from django.conf import settings

from django.utils.timezone import now
from django.utils import dateformat

# from django.contrib.sites.shortcuts import get_current_site

from django.shortcuts import get_object_or_404

from django.db.models import Sum

from django.http import FileResponse

# Create your views here.
# https://github.com/axelpale/minimal-django-file-upload-example/blob/master/src/for_django_3-0/myapp/views.py
# https://www.django-rest-framework.org/tutorial/quickstart/#serializers
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

class FolderViewSet(viewsets.ModelViewSet):
	queryset = Folder.objects.all()
	serializer_class = FolderSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

	def perform_create(self, serializer):
		serializer.save()

class YTLinkViewSet(viewsets.ModelViewSet):
	queryset = YTLink.objects.all()
	serializer_class = YTLinkSerializer
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



#@login_required
def index(request):
	if request.user.is_authenticated:
		form = UploadFileForm()
		folderform = FolderForm()
		msg = ""
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
							parentdir = form.cleaned_data['parentdir']
							newdoc = Document(docfile=f, parentdir=parentdir)
							newdoc.save()
						return redirect('index')

				###   YOUTUBE LINK UPLOAD   ###

				else:
					form = YTLinkForm(request.POST)
					if form.is_valid():
						parentdir = form.cleaned_data['parentdir']
						link = form.cleaned_data['link']
						newdoc = YTLink(link=link, parentdir=parentdir)
						newdoc.save()
						return redirect('index')
			
			###   CREATE FOLDER   ###

			elif 'folder_create' in request.POST:

				folderform = FolderForm(request.POST)
				#print(folderform.is_valid(), folderform.errors)
				if folderform.is_valid():
					parentdir = folderform.cleaned_data['parentdir']
					name = folderform.cleaned_data['name']
					newfolder = Folder(parentdir=parentdir, name=name)
					newfolder.save()
					return redirect('index')

			###   DELETE FILE   ###

			elif 'doc_delete' in request.POST:
				doc = Document.objects.get(id=int(request.POST['doc_pk']))
				filename = os.path.dirname(os.path.abspath(__file__))+'/../media_cdn/'+str(doc.docfile)
				#print("Deleting", 'media_cdn/'+str(doc.docfile))
				#print("Deleting", filename)
				os.remove(filename)

				# IN CASE OF PDF'S REMOVE ALL "file.pdf____0123"
				pathtofile = ''.join(str(doc.docfile).split("/")[:-1])
				dir_name = os.path.dirname(os.path.abspath(__file__))+'/../media_cdn/'+pathtofile
				#print(dir_name)
				test = os.listdir(dir_name)
				#print(test)
				for item in test:
					#print(item, item.startswith((str(doc.docfile).split("/")[-1])+"____"))
					if item.startswith((str(doc.docfile).split("/")[-1])+"____"):
						os.remove(os.path.join(dir_name, item))

				msg = "Deleted file " + str(doc.docfile)

				doc.delete()

			###   DELETE LINK   ###

			elif 'link_delete' in request.POST:
				doc = YTLink.objects.get(id=int(request.POST['link_pk']))
				doc.delete()

			###   DELETE FOLDER   ###

			elif 'folder_delete' in request.POST:
				folderid = request.POST['folder_pk']
				folder = Folder.objects.get(pk=folderid)
				folder.delete()

			###   DOWNLOAD FILE   ###

			elif 'doc_download' in request.POST:
				return serve_file(request, {})

		###   VIEW HANDLING   ###

		documents = Document.objects.all()
		folders = Folder.objects.all()

		if Folder.objects.all().count() == 0:
			print(Folder.objects.all().count() + "folders. Creating root")
			root = Folder(name="", )
			root.save()

		root = Folder.objects.get(name="")

		tree = dir_tree_builder(root, "Root")

		context = {'tree': tree, 'folders': folders, 'documents': documents, 'form': form, 'folderform': folderform, 'msg': msg}

		return render(request, 'index.html', context)
	return redirect('/api-auth/login/?next=/')

def dir_tree_builder(dir, root="Folder"):
	tree = [(root, dir)] # type, content, EXAMPLE-> (YTLink, <YTLink object...>,)
	# print(dir.folder_set.all())

	documents = dir.document_set.all()
	for document in documents:
		tree += [('Document', document)]

	links = dir.ytlink_set.all()
	for link in links:
		tree += [('YTLink', link)]
	
	children = dir.folder_set.all()
	for child in children:
		tree += dir_tree_builder(child)

	tree += [('CloseFolder', None)]

	return tree

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
				print(entryform)
				if entryform.is_valid():
					print(entryform.cleaned_data)
					program = entryform.cleaned_data['program']
					duration = entryform.cleaned_data['duration']

					if(entryform.cleaned_data['content'] != None):
						print('content')
						content = entryform.cleaned_data['content']
						entry = ProgramEntry(program=program, content=content, duration=duration)
						entry.save()
					elif(entryform.cleaned_data['ytcontent'] != None):
						print('ytcontent')
						ytcontent = entryform.cleaned_data['ytcontent']
						#obj = YTLink.objects.get(id=ytcontent)
						entry = ProgramEntry(program=program, ytcontent=ytcontent, duration=ytcontent.duration + 10)
						entry.save()
					try:
						print(entry)
					except:
						pass
						
			elif 'program_delete' in request.POST:
				programid = request.POST['program']
				program = ContentProgram.objects.get(pk=programid)
				program.delete()
			elif 'entry_delete' in request.POST:
				entryid = request.POST['entry']
				entry = ProgramEntry.objects.get(pk=entryid)
				entry.delete()
			elif 'group_delete' in request.POST:
				groupid = request.POST['group']
				group = AgentGroup.objects.get(pk=groupid)
				group.delete()
				return redirect('space_view')
			return redirect('group_individual', id)

		actualtime = dateformat.format(now(), 'Y-m-d H:i:s')
		entries = ProgramEntry.objects.all()
		group = get_object_or_404(AgentGroup, pk=id)
		documents = Document.objects.all()
		ytlinks = YTLink.objects.all()
		context = {'actualtime': actualtime, 'entries': entries, 'ytlinks': ytlinks, 'documents': documents, 'group': group, 'programform': programform, 'entryform': entryform}
		return render(request, "group_individual.html", context)
	return redirect('/api-auth/login/?next=/spaces')

def document_individual(request, id):
	if request.user.is_authenticated:
		document = get_object_or_404(Document, id=id)
		stats = document.stats_set.all().order_by('agent')

		attention_avg = 0
		attention_total = 0
		frames = 0
		for stat in stats:
			attention_total += stat.attention
			frames += stat.frames
		if frames != 0:
			attention_avg = "{:.2f}".format(100 * attention_total / frames)

		data1 = []
		labels1 = []

		data4 = [0,0,0,0,0,0,0,0]

		if frames == 0:
			frames = 1
		i = 1
		for stat in stats:
			# data1

			if str(stat.agent.id) not in labels1:
				labels1.append(str(stat.agent.id))
			
			viewtime = ( document.viewtime * stat.frames ) / frames

			if len(data1)<i:
				data1.append(viewtime)
			else:
				data1[stat.agent.id] += viewtime
			i += 1

			## data4
			data4[0] += stat.neutral
			data4[1] += stat.happiness
			data4[2] += stat.surprise
			data4[3] += stat.sadness
			data4[4] += stat.anger
			data4[5] += stat.disgust
			data4[6] += stat.fear
			data4[7] += stat.contempt

		#print(data4)

		for idx, emotion in enumerate(data4):
			data4[idx] = 100 * emotion / frames
		
		view_count = stats.values('person').distinct().count()

		data2 = []
		data3 = []

		for agent_id in labels1:
			agent_view_count = stats.filter(agent=agent_id).values('person').distinct().count()
			data2.append(agent_view_count)

			agent_attention = stats.filter(agent=agent_id).aggregate(Sum('attention'))['attention__sum']
			agent_frames = stats.filter(agent=agent_id).aggregate(Sum('frames'))['frames__sum']
			agent_attention_per = (100 * agent_attention) / agent_frames
			data3.append(agent_attention_per)

		#print(labels1)
		#print(data1)
		#print(data2)
		#print(data3)
		#print(data4)

		context = {'document': document, 'stats': stats, 'attention_avg': attention_avg,
					'view_count': view_count, 'data1': data1, 'labels1': labels1,
					'data2': data2, 'data3': data3, 'data4': data4}
		return render(request, "document_individual.html", context)
	return redirect('/api-auth/login/?next=/')

def agent_view(request):

	if request.user.is_authenticated:
		form = AgentForm()
		if request.method == 'POST':

			###   AGENT UPLOAD   ###

			if 'agent_upload' in request.POST:
				form = AgentForm(request.POST)
				#print(request.POST)
				if form.is_valid():
					id = form.cleaned_data['id']
					name = form.cleaned_data['name']
					group = form.cleaned_data['group']
					#print(id,name,group)
					agent = Agent(id=id, name=name, group=group)
					#print(agent)
					agent.save()
					return redirect('agent_view')

			###   DELETE AGENT   ###

			elif 'agent_delete' in request.POST:
				agent = Agent.objects.get(id=int(request.POST['agent_pk']))
				agent.delete()

		###   VIEW HANDLING   ###

		agents = Agent.objects.all()
		groups = AgentGroup.objects.all()

		today =  datetime.now()

		context = {'agents': agents, 'groups': groups, 'form': form, 'today': today}

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
			# JA N SEI PQ E QUE ISTO NAO FUNCIONOU !!!!!!!!!
			#elif 'group_submit' in request.POST:
			#	groupform = AgentGroupForm(request.POST)
			#	if groupform.is_valid():
			#		name = groupform.cleaned_data['name']
			#		space = groupform.cleaned_data['space']
			#		group = AgentGroup(name=name, space=space)
			#		group.save()
			#		return redirect('space_view')
			elif 'space_delete' in request.POST:
				spaceid = request.POST['space']
				space = Space.objects.get(pk=spaceid)
				print(space)
				space.delete()
		agents = Agent.objects.all()
		groups = AgentGroup.objects.all()
		spaces = Space.objects.all()
		context = {'spaces': spaces, 'groups': groups, 'agents': agents,
			'spaceform': spaceform, 'groupform': groupform}
		return render(request, 'space_view.html', context)
	return redirect('/api-auth/login/?next=/spaces')

# JA N SEI PQ E QUE ISTO FOI NECESSARIO
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


def viewfile_view(request, slug):
	print("VIEW", settings.MEDIA_ROOT +'/media/'+ slug)
	try:
		isPDF = True
		try:
			inputpdf = PdfFileReader(open(settings.MEDIA_ROOT +'/media/'+ slug, "rb"))
		except:
			isPDF = False
		print("isPDF", isPDF)
		if isPDF:
			return FileResponse(open(settings.MEDIA_ROOT +'/media/'+ slug, 'rb'), content_type='application/pdf')
		else:
			return FileResponse(open(settings.MEDIA_ROOT +'/media/'+ slug, 'rb'))
	except FileNotFoundError:
		return HttpResponseNotFound('<h1>File not found</h1>')


#@login_required
def qr_view(request, slug):
	return serve_qr(request, {}, slug)
#@login_required
def serve_qr(request, context, slug=''):
	#if request.user.is_authenticated:
	#print(request)
	#print(request.POST)
	#print('DOWNLOAD URL')
	#print('AAAA', slug)
	filename = settings.MEDIA_ROOT +'/'+'qrcodes/'+slug
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


#@login_required
def file_view(request, slug):
	return serve_file(request, {}, slug)
#@login_required
def serve_file(request, context, slug=''):
	try:
		#if request.user.is_authenticated:
		#print(request)
		#print(request.POST)
		if request.POST and 'doc_pk' in request.POST:
			print('DOWNLOAD BUTTON')
			doc = Document.objects.get(id=int(request.POST['doc_pk']))
			filename = settings.MEDIA_ROOT +'/'+ doc.docfile.name
		else:
			try: # DOC EXISTS AND WILL BE DOWNLOADED
				#print('DOWNLOAD URL')
				#print('AAAA', slug)
				doc = Document.objects.get(docfile= ('media/'+slug) )
				#print('DOC', doc)
				filename = settings.MEDIA_ROOT +'/'+ doc.docfile.name
			except: # DOC DOESN'T EXIST, WHICH MEANS IT'S A PAGE OF A PDF
				filename = settings.MEDIA_ROOT +'/media/' + slug
				
		print('OLEOLE', filename)
		response = HttpResponse(content_type='application/force-download')
		downloadname = filename.split('/')[-1]
		response['Content-Disposition']='attachment;filename="%s"'%downloadname
		response["X-Sendfile"] = filename
		response['Content-length'] = os.path.getsize(filename)
		#print(os.path.getsize(filename))
		return response
		#return redirect('index')
		#pass
	except:
		return HttpResponseNotFound('<h1>File not found</h1>')


def control_view(request, hash):

	if AgentUpdate.objects.all().filter(url_hash = hash).count() != 0:

		update = AgentUpdate.objects.get(url_hash=hash)
		agent = update.agent


		# FINDING THE PROGRAM THAT IS RUNNING ON THE AGENT
		prev_program = ''
		for program in agent.group.contentprogram_set.all():
			#print("it")
			if prev_program != '':
				#print(program.start_date, ">     ", prev_program.start_date, "       ?", program.start_date > prev_program.start_date)
				#print(program.start_date, "< now:", now(), "?", program.start_date < now())
				if program.start_date > prev_program.start_date and\
					program.start_date < now():
						#print("Actual program", program.start_date)
						prev_program = program
			elif program.start_date < now():
				#print("Actual program", program.start_date)
				prev_program = program


		if request.method == 'POST':

			#print(request.POST)
			#print("Agent", agent.id)

			content_pk = request.POST['content_pk']
			#print("Content", content_pk)
			ytcontent_pk = request.POST['ytcontent_pk']
			#print("YTContent", ytcontent_pk)

			if update.expires_max == None:
				update.expires_max = now() + timedelta(minutes=20)
			
			entry_pk = request.POST['entry_pk']
			entry = ProgramEntry.objects.get(id=entry_pk)
			update.expires = now() + timedelta(seconds=60+entry.duration)

			if content_pk:
				update.content = Document.objects.get(pk=content_pk)
				update.ytcontent = None
			elif ytcontent_pk:
				update.content = None
				update.ytcontent = YTLink.objects.get(pk=ytcontent_pk)

			update.content_confirm = False
			update.contentpage = request.POST['content_page']
			update.save()

		context = {'range': range(1, 100), 'program': prev_program}
		return render(request, 'control.html', context)
	
	else:
		return HttpResponseNotFound('<h1>Read the QR code again</h1>')