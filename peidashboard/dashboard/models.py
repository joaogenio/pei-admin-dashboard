from django.db import models

from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

from django.conf import settings

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
    docfile = models.FileField(unique=True, upload_to='media')
    title = models.CharField(max_length=100, blank=True, default='')
    #owner = models.ForeignKey('auth.User', related_name='documents', on_delete=models.CASCADE)
    downloadlink = models.URLField(default='')

    def save(self, path='', *args, **kwargs):
        super(Document, self).save(*args, **kwargs)
        self.downloadlink = 'http://'+path+'/download/'+self.docfile.name.split('/')[-1]
        super(Document, self).save(*args, **kwargs)

    #def get_absolute_url(self):
    #    #return 'download/' + self.docfile.name.split('/')[-1]
    #    return build_absolute_uri(reverse('file_view', (), {'slug': self.docfile.name.split('/')[-1]}))
    