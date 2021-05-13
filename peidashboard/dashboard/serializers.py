from django.contrib.auth.models import User, Group
from rest_framework import serializers

from .models import Document, Snippet, Crop, LANGUAGE_CHOICES, STYLE_CHOICES


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(
        view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ['url', 'id', 'highlight', 'owner',
                  'title', 'code', 'linenos', 'language', 'style']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name='snippet-detail', read_only=True)

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'snippets']


class CropSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Crop
        fields = ['url', 'id', 'cropfile', 'content']


class DocumentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=Document
        fields=['url', 'id', 'title', 'downloadlink', 'docfile']
        extra_kwargs={
            'docfile': {'write_only': True}
        }

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Group
        fields=['url', 'name']
