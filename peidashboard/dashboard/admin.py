from django.contrib import admin

from .models import Snippet, Document

# Register your models here.

admin.site.register(Snippet)
admin.site.register(Document)
