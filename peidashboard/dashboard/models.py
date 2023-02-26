from django.db import models
from django.db.models.base import Model
from django.db.models.deletion import CASCADE, SET_NULL

# from pygments.lexers import get_all_lexers
# from pygments.styles import get_all_styles

# from pygments.lexers import get_lexer_by_name
# from pygments.formatters.html import HtmlFormatter
# from pygments import highlight

from django.conf import settings

import os

from datetime import datetime

import time

from jsonfield import JSONField

from django.utils.timezone import now

import hashlib

import qrcode

from PyPDF2 import PdfFileWriter, PdfFileReader

import urllib.request
import json
import urllib
import pprint

import pafy

from django.utils.functional import keep_lazy_text

class Folder(models.Model):
    parentdir = models.ForeignKey("Folder", on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

class YTLink(models.Model):
    parentdir = models.ForeignKey(Folder, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    link = models.URLField(default='', unique=True)
    title = models.CharField(max_length=100, blank=True, default='')
    duration = models.PositiveIntegerField()
    # STATISTICS
    viewtime = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):

        link = self.link # https://www.youtube.com/watch?v=iEVdFWgx6_0&list=...&index=...
        VideoID = link.split("&")[0].split("=")[-1]
        #print(VideoID)

        video = pafy.new(link)
        print(video.duration)
        split = (""+video.duration).split(':')
        print( (int(split[0])*3600 + int(split[1])*60 + int(split[2])), "seconds")
        self.duration = int(split[0])*3600 + int(split[1])*60 + int(split[2])

        params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % VideoID}
        url = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        url = url + "?" + query_string

        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            pprint.pprint(data)
            title = data['title']
            #print(title)
            self.title = title
        
        super(YTLink, self).save(*args, **kwargs)
    
    @property
    def pretty_duration(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.duration))
    
    @property
    def pretty_viewtime(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.viewtime))

class Document(models.Model):
    parentdir = models.ForeignKey(Folder, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    docfile = models.FileField(upload_to='media', unique=True)
    docname = models.CharField(max_length=100, blank=True, default='')
    downloadlink = models.URLField(editable=False, default='')
    viewlink = models.URLField(editable=False, default='')
    # STATISTICS
    viewtime = models.PositiveIntegerField(default=0)
    pages = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['docfile']
    
    @keep_lazy_text
    def get_valid_filename(s):
        """
        Returns the given string converted to a string that can be used for a clean
        filename. Specifically, leading and trailing spaces are removed; other
        spaces are converted to underscores; and anything that is not a unicode
        alphanumeric, dash, underscore, or dot, is removed.
        >>> get_valid_filename("john's portrait in 2004.jpg")
        'johns_portrait_in_2004.jpg'
        """
        s = force_text(s).strip().replace(' ', '_')
        return re.sub(r'(?u)[^-\w.]', '', s)

    def save(self, *args, **kwargs):

        super(Document, self).save(*args, **kwargs)
        
        #print(self.docfile.name)

        # SET A DOWNLOAD LINK (AND VIEW)
        self.downloadlink = 'http://' + \
            settings.ALLOWED_HOSTS[0]+'/download/' + \
            self.docfile.name.split('/')[-1]
        
        self.viewlink = 'http://' + \
            settings.ALLOWED_HOSTS[0]+'/view/' + \
            self.docfile.name.split('/')[-1]
        
        self.docname = self.docfile.name.split('/')[-1]

        super(Document, self).save(*args, **kwargs)

        # ONCE DOC IS SAVED, IF IT'S PDF, THEN SEPARATE
        isPDF = True
        pages = 0
        target = os.path.dirname(os.path.abspath(__file__))+'/../media_cdn/'+str(self.docfile)
        #print(target)
        try:
            inputpdf = PdfFileReader(open(target, "rb"))
            
            for i in range(inputpdf.numPages):
                output = PdfFileWriter()
                output.addPage(inputpdf.getPage(i))
                with open("%s____%04d" % (target, i+1), "wb") as outputStream:
                    output.write(outputStream)
                pages += 1
        except:
            #print("not a PDF file")
            isPDF = False

        if isPDF:
            self.pages = pages
            # SAVE AGAIN BECAUSE OF PAGES
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
            newgroup = AgentGroup(
                name=groupname, space=Space.objects.get(pk=self.pk))
            newgroup.save()


class AgentGroup(models.Model):
    name = models.CharField(max_length=100)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)

    class Meta:
        ordering = ['space', 'name']


class Agent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey(AgentGroup, null=True, on_delete=models.SET_NULL)
    # USE agent.update TO ACCESS THE CORRESPONDING AgentUpdate INSTANCE

    class Meta:
        ordering = ['group', 'id']

    def save(self, *args, **kwargs):
        super(Agent, self).save(*args, **kwargs)
        print(AgentUpdate.objects.filter(pk=self.pk))
        print(AgentUpdate.objects.filter(pk=self.pk).count())
        if AgentUpdate.objects.filter(pk=self.pk).count() == 0:
            newhash = str(  hashlib.md5( ( str(self.pk)+str(now()) ).encode() ).hexdigest()  )
            print("newhash", newhash)
            update = AgentUpdate(
                agent=Agent.objects.get(pk=self.pk),
                url_hash=newhash,
                content_confirm=True
            )
            update.save()
        else:
            update = AgentUpdate.objects.get(pk=self.pk)
            update.content_confirm = True
            update.save()


class Person(models.Model):
    descriptor = JSONField()


class Stats(models.Model):
    person = models.ForeignKey(Person, null=True, on_delete=models.CASCADE)

    content = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    ytcontent = models.ForeignKey(YTLink, null=True, on_delete=models.CASCADE)

    agent = models.ForeignKey(Agent, null=True, on_delete=models.CASCADE)
    attention = models.FloatField()
    neutral = models.PositiveIntegerField(default=0)
    happiness = models.PositiveIntegerField(default=0)
    surprise = models.PositiveIntegerField(default=0)
    sadness = models.PositiveIntegerField(default=0)
    anger = models.PositiveIntegerField(default=0)
    disgust = models.PositiveIntegerField(default=0)
    fear = models.PositiveIntegerField(default=0)
    contempt = models.PositiveIntegerField(default=0)
    frames = models.PositiveIntegerField(default=0)

    # 2 NULLS,  2 NAO NULLS. ESTES CASOS NAO SERVEM
    # vvvv Caso eu faça asneira nos forms vvvv
    def save(self, *args, **kwargs):
        if not (self.content == None and self.ytcontent == None) and not (self.content != None and self.ytcontent != None):
            super(Stats, self).save(*args, **kwargs)

from humanfriendly import format_timespan

# USE agent.update TO ACCESS THIS !!!!!!!!!!!
class AgentUpdate(models.Model):
    agent = models.OneToOneField(
        Agent,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='update'
    )
    url_hash = models.CharField(max_length=32, unique=True)
    expires = models.DateTimeField(null=True)
    expires_max = models.DateTimeField(
        null=True)  # given first interaction, sets this to avoid continuous "dominance"

    # When a request is made, one of the following 2 fields HAS TO BE NULL!!!!!!!!!!!!!!
    content = models.ForeignKey(Document, null=True, on_delete=models.SET_NULL)
    ytcontent = models.ForeignKey(YTLink, null=True, on_delete=models.SET_NULL)

    contentpage = models.IntegerField(default=0)
    content_confirm = models.BooleanField(default=False)

    @property
    def timesince(self): # IN SECONDS
        try:
            return ( now() - self.expires ).total_seconds()
        except:
            return None

    @property
    def pretty_timesince(self): # Y M D H m s
        ts = self.timesince
        if ts != None:
            return format_timespan(ts)
        return None


    # vvvv Caso eu faça asneira nos forms vvvv
    def save(self, *args, **kwargs):
        # 2 NULLS,  2 NAO NULLS. ESTES CASOS NAO SERVEM
        #if not (self.content == None and self.ytcontent == None) and not (self.content != None and self.ytcontent != None):
        # ________  2 NAO NULLS. ESTE_ CASO_ NAO SERVE_
        if not (self.content != None and self.ytcontent != None):
            
            if AgentUpdate.objects.filter(pk=self.pk).count() != 0:
                old = AgentUpdate.objects.get(pk=self.pk)
                dirname = os.path.dirname(__file__)

                print('old', old.url_hash, '\nnew', self.url_hash)
                if old.url_hash != self.url_hash:
                    # DELETE PREVIOUS QR CODE
                    print("deleting qr code")
                    oldfile = os.path.join(dirname, '../media_cdn/qrcodes/' + old.url_hash + '.png')
                    try:
                        os.remove(oldfile)
                    except:
                        pass

                    # NEW QR CODE
                    print("creating qr code")
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_H,
                        box_size=3,
                        border=1,
                    )
                    url = 'http://' + settings.ALLOWED_HOSTS[0] + '/control/'
                    print(url)
                    qr.add_data(url + self.url_hash)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
                    filename = os.path.join(dirname, '../media_cdn/qrcodes/' + self.url_hash + '.png')
                    img.save(filename)
            
            super(AgentUpdate, self).save(*args, **kwargs)


class ContentProgram(models.Model):
    group = models.ForeignKey(AgentGroup, on_delete=CASCADE)
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(default=now)

    class Meta:
        ordering = ['start_date', 'name']


class ProgramEntry(models.Model):
    program = models.ForeignKey(ContentProgram, on_delete=models.CASCADE)
    
    content = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    ytcontent = models.ForeignKey(YTLink, null=True, on_delete=models.CASCADE)

    duration = models.PositiveIntegerField()

    # 2 NULLS,  2 NAO NULLS. ESTES CASOS NAO SERVEM
    # vvvv Caso eu faça asneira nos forms vvvv
    def save(self, *args, **kwargs):
        if not (self.content == None and self.ytcontent == None) and not (self.content != None and self.ytcontent != None):
            super(ProgramEntry, self).save(*args, **kwargs)

    @property
    def pretty_duration(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.duration))


class Crop(models.Model):
    cropfile = models.FileField(blank=True, upload_to='crops')

    content = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    ytcontent = models.ForeignKey(YTLink, null=True, on_delete=models.CASCADE)

    agentid = models.ForeignKey(Agent, on_delete=CASCADE)
    interactiontime = models.IntegerField(blank=True, default=0)

    # 2 NULLS,  2 NAO NULLS. ESTES CASOS NAO SERVEM
    # vvvv Caso eu faça asneira nos forms vvvv
    def save(self, *args, **kwargs):
        if not (self.content == None and self.ytcontent == None) and not (self.content != None and self.ytcontent != None):
            
            #print("Uploading crop...")
            super(Crop, self).save(*args, **kwargs)

            print("ola")

            if self.content != None:
                self.content.viewtime += self.interactiontime
                self.content.save()
            elif self.ytcontent != None:
                self.ytcontent.viewtime += self.interactiontime
                self.ytcontent.save()

            if self.cropfile == '':
                crop = Crop.objects.get(id=int(self.pk))
                crop.delete()

