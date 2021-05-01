from django.shortcuts import render, redirect
#from django.http import HttpResponseRedirect

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions

from .serializers import UserSerializer, GroupSerializer
from .forms import UploadFileForm
from .models import Document


#from django.http import HttpResponse, JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#from rest_framework.parsers import JSONParser

from .models import Snippet
from .serializers import SnippetSerializer

from rest_framework.decorators import api_view

#from django.http import Http404
#from rest_framework.views import APIView
from rest_framework.response import Response
#from rest_framework import status

#from rest_framework import mixins
#from rest_framework import generics

from .serializers import UserSerializer

from .permissions import IsOwnerOrReadOnly

from rest_framework.reverse import reverse

from rest_framework import renderers

from rest_framework import viewsets

from rest_framework.decorators import action

# Create your views here.
# https://github.com/axelpale/minimal-django-file-upload-example/blob/master/src/for_django_3-0/myapp/views.py
# https://www.django-rest-framework.org/tutorial/quickstart/#serializers
# https://www.django-rest-framework.org/tutorial/

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'snippets': reverse('snippet-list', request=request, format=format)
    })

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

def index(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		#Document.objects.all().delete()
		if form.is_valid():
			newdoc = Document(docfile=request.FILES['docfile'])
			newdoc.save()
			return redirect('index')
	else:
		form = UploadFileForm()

	documents = Document.objects.all()

	context = {'documents': documents, 'form': form}

	return render(request, 'index.html', context)
