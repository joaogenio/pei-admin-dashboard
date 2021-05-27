from django.contrib.auth.models import User, Group
from rest_framework import serializers

from .models import Space, AgentGroup, Agent, AgentUpdate, Document, Snippet, Crop, LANGUAGE_CHOICES, STYLE_CHOICES


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

class SpaceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Space
        fields = ['url', 'id', 'name']

class AgentGroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AgentGroup
        fields = ['url', 'id', 'name', 'space']

class AgentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Agent
        fields = ['url', 'id', 'name', 'group']

class AgentUpdateSerializer(serializers.HyperlinkedModelSerializer):
    agent = AgentSerializer(read_only=True)

    class Meta:
        model = AgentUpdate
        fields = ['url', 'agent', 'contentid', 'contentname', 'content_confirm']
        extra_kwargs={
            'contentname': {'read_only': True}
        }

class DocumentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=Document
        fields=['url', 'id', 'title', 'downloadlink', 'docfile']
        extra_kwargs={
            'docfile': {'write_only': True}
        }

class CropSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Crop
        fields = ['url', 'id', 'cropfile', 'content', 'agentid', 'interactiontime']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Group
        fields=['url', 'name']
