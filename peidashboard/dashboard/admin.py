from django.contrib import admin

from .models import AgentGroup, ContentProgram, Document

# Register your models here.

admin.site.register(Document)
admin.site.register(AgentGroup)
admin.site.register(ContentProgram)
