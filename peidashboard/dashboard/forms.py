from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(label='Title', required=False, max_length=100)
    docfile = forms.FileField(label='Insert file', widget=forms.ClearableFileInput(attrs={'multiple': True}))