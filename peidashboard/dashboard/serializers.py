from django.contrib.auth.models import User, Group
from rest_framework import serializers

from .models import *

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

class DocumentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=Document
        fields=['url', 'id', 'title', 'downloadlink', 'docfile', 'docname', 'youtubelink']
        extra_kwargs={
            'docfile': {'write_only': True},
            'docname': {'read_only': True}
        }

class ProgramEntrySerializer(serializers.HyperlinkedModelSerializer):
    doc = DocumentSerializer()

    class Meta:
        model = ProgramEntry
        fields = ['url', 'program', 'doc', 'duration']

class ContentProgramSerializer(serializers.HyperlinkedModelSerializer):
    programentry_set = ProgramEntrySerializer(read_only=True, many=True)

    class Meta:
        model = ContentProgram
        fields = ['url', 'group', 'name', 'start_date', 'programentry_set']

class AgentGroupSerializer(serializers.HyperlinkedModelSerializer):
    contentprogram_set = ContentProgramSerializer(read_only=True, many=True)

    class Meta:
        model = AgentGroup
        fields = ['url', 'id', 'name', 'space', 'contentprogram_set']

class AgentSerializer(serializers.HyperlinkedModelSerializer):
    group = AgentGroupSerializer()

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

class StatsSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Stats
        fields = ['url', 'id', 'agent', 'content', 'person']

class PersonSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Person
        fields = ['url', 'id', 'descriptor']

class CropSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Crop
        fields = ['url', 'id', 'cropfile', 'content', 'agentid', 'interactiontime']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Group
        fields=['url', 'name']
