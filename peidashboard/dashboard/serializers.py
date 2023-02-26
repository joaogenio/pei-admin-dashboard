from django.contrib.auth.models import User, Group
from rest_framework import serializers

from .models import *

class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['url', 'id', 'username']

class SpaceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Space
        fields = ['url', 'id', 'name']

class FolderSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=Folder
        fields=['url', 'id', 'parentdir', 'created', 'name']

class YTLinkSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=YTLink
        fields=['url', 'id', 'parentdir', 'added', 'link', 'title', 'viewtime']

class DocumentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=Document
        fields=['url', 'id', 'parentdir', 'added', 'downloadlink', 'viewlink', 'docname', 'viewtime', 'pages']
        extra_kwargs={
            'docname': {'read_only': True}
        }

class ProgramEntrySerializer(serializers.HyperlinkedModelSerializer):
    content = DocumentSerializer()
    ytcontent = YTLinkSerializer()

    class Meta:
        model = ProgramEntry
        fields = ['url', 'program', 'content', 'ytcontent', 'duration']

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

class SimpleAgentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Agent
        fields = ['url', 'id', 'name', 'group']

class AgentUpdateSerializer(serializers.HyperlinkedModelSerializer):
    agent = SimpleAgentSerializer(read_only=True)
    content = DocumentSerializer()
    ytcontent = YTLinkSerializer()

    class Meta:
        model = AgentUpdate
        fields = ['url', 'agent', 'url_hash', 'expires', 'expires_max', 'content', 'ytcontent', 'contentpage', 'content_confirm']
        extra_kwargs={
            'contentname': {'read_only': True}
        }

class StatsSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Stats
        fields = ['url', 'id', 'agent', 'content', 'ytcontent', 'person',
            'attention', 'neutral', 'happiness', 'surprise',
            'sadness', 'anger', 'disgust', 'fear', 'contempt', 'frames']

class PersonSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Person
        fields = ['url', 'id', 'descriptor']

class CropSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Crop
        fields = ['url', 'id', 'cropfile', 'content', 'ytcontent', 'agentid', 'interactiontime']
