from rest_framework import fields
from dashboard.models import *
from django import forms
from django.forms.models import ModelForm
from django.forms import ValidationError

class FolderForm(forms.Form):
    parentdir = forms.ModelChoiceField(queryset=Folder.objects.all()) # required = True
    name = forms.CharField(label='Name', max_length=100)

    def clean(self):
        cd = self.cleaned_data

        for folder in Folder.objects.all():
            if folder.name == cd.get("name"):
                raise ValidationError({'name': ["Sorry. You can't name another folder '"+ folder.name +"'.",]})

class YTLinkForm(forms.Form):
    parentdir = forms.ModelChoiceField(queryset=Folder.objects.all())
    link = forms.URLField(empty_value='', required=False)

class UploadFileForm(forms.Form):
    parentdir = forms.ModelChoiceField(queryset=Folder.objects.all())
    docfile = forms.FileField(label='Insert file', widget=forms.ClearableFileInput(attrs={'multiple': True}))

class SpaceForm(ModelForm):
    class Meta:
        model = Space
        fields = ['name']

class AgentGroupForm(ModelForm):
    class Meta:
        model = AgentGroup
        fields = ['name', 'space']

class AgentForm(forms.Form):
    id = forms.IntegerField(min_value=0)
    name = forms.CharField(label='Name', required=True, max_length=100)
    group = forms.ModelChoiceField(queryset=AgentGroup.objects.all())

    def clean(self):
        cd = self.cleaned_data

        if Agent.objects.filter(pk=cd.get("id")).count() > 0:
            raise ValidationError("Agent with this Id already exists.")
        for agent in Agent.objects.all():
            if agent.name == cd.get("name"):
                raise ValidationError("Agent with this Name already exists.")
        
        return cd

class ProgramEntryForm(ModelForm):
    content = forms.ModelChoiceField(queryset=Document.objects.all(), required=False)
    ytcontent = forms.ModelChoiceField(queryset=YTLink.objects.all(), required=False)

    class Meta:
        model = ProgramEntry
        fields = ['program', 'content', 'ytcontent', 'duration']

class ContentProgramForm(ModelForm):
    class Meta:
        model = ContentProgram
        fields = ['group', 'name', 'start_date']
