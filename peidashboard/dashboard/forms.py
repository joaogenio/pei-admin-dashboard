from rest_framework import fields
from dashboard.models import Agent, AgentGroup, ContentProgram, ProgramEntry, Space
from django import forms
from django.forms.models import ModelForm
from django.forms import ValidationError

class UploadFileForm(forms.Form):
    title = forms.CharField(label='Title', required=False, max_length=100)
    docfile = forms.FileField(label='Insert file', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    youtubelink = forms.URLField(empty_value='', required=False)

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
    class Meta:
        model = ProgramEntry
        fields = ['program', 'doc', 'duration']

class ContentProgramForm(ModelForm):
    class Meta:
        model = ContentProgram
        fields = ['group', 'name', 'start_date']
