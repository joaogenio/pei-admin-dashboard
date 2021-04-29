from django.shortcuts import render, redirect
#from django.http import HttpResponseRedirect
from .forms import UploadFileForm
from .models import Document

# Create your views here.

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
