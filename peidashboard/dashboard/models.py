from django.db import models
from django.db.models.deletion import SET_NULL

from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

from django.conf import settings

import os

from datetime import datetime

import time

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
    highlighted = models.TextField()

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,
                                full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)

class Document(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    docfile = models.FileField(unique=True, upload_to='media')
    docname = models.CharField(max_length=100, blank=True, default='')
    title = models.CharField(max_length=100, blank=True, default='')
    downloadlink = models.URLField(editable=False, default='')
    # STATISTICS
    #viewcount = models.PositiveIntegerField(default=0)
    viewtime = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created']

    def save(self, *args, **kwargs):
        self.downloadlink = 'http://'+settings.ALLOWED_HOSTS[0]+'/download/'+self.docfile.name.split('/')[-1]
        self.docname = self.docfile.name.split('/')[-1]
        super(Document, self).save(*args, **kwargs)

    @property
    def pretty_viewtime(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.viewtime))

class Space(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        super(Space, self).save(*args, **kwargs)
        groupname = "Grp_" + self.name
        if AgentGroup.objects.filter(name=groupname).count() == 0:
            newgroup = AgentGroup(name=groupname, space=Space.objects.get(pk=self.pk))
            newgroup.save()

class AgentGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)

    class Meta:
        ordering = ['space', 'name']

class Agent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey(AgentGroup, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['group', 'name']
    
    def save(self, *args, **kwargs):
        super(Agent, self).save(*args, **kwargs)
        if AgentUpdate.objects.filter(pk=self.pk).count() == 0:
            update = AgentUpdate(agent=Agent.objects.get(pk=self.pk), content_confirm=False)
            update.save()
        else:
            update = AgentUpdate.objects.get(pk=self.pk)
            update.content_confirm = False
            update.save()

class AgentUpdate(models.Model):
    agent = models.OneToOneField(
        Agent,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    urltoken = models.CharField(max_length=100, unique=True)
    token_confirm = models.BooleanField(default=False)
    contentid = models.ForeignKey(Document, null=True, on_delete=models.SET_NULL)
    contentname = models.CharField(max_length=100, blank=True, default='')
    content_confirm = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        doc = Document.objects.get(pk=self.contentid.id)
        self.contentname = doc.docfile.name.split('/')[-1]
        super(AgentUpdate, self).save(*args, **kwargs)

class ContentProgram(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateTimeField(default=datetime.now)
    doc_order = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['start_date', 'name']

class Crop(models.Model):
    cropfile = models.FileField(blank=True, upload_to='crops')
    content = models.TextField()
    agentid = models.IntegerField()
    interactiontime = models.IntegerField(blank=True, default=0)

    def save(self, *args, **kwargs):
        #print("Uploading crop...")
        super(Crop, self).save(*args, **kwargs)

        # DO STUFF WITH THE CROP // IMAGE MANIPULATION STUFF        

        print("ola")

        if Document.objects.filter(docname=self.content).count() != 0:
            targetdoc = Document.objects.get(docname=self.content)
            targetdoc.viewtime += self.interactiontime
            targetdoc.save()

        # DELETE ACTUAL FILE

        if self.cropfile != '':
            print(self.cropfile)
            filename = os.path.dirname(os.path.abspath(__file__))+'/../media_cdn/'+str((self.cropfile))
            print(filename)
            os.remove(filename)
        else:
            print("no file provided")

        # DELETE ENTRY FROM DB

        #print("Self", self.pk)
        crop = Crop.objects.get(id=int(self.pk))
        crop.delete()
        Crop.objects.all().delete()
        #print("Deleting crop...")
        #print("Crops", Crop.objects.all())