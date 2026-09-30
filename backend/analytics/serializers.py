from rest_framework import serializers

from .models import AIConversation, AIMessage, AIToolCall


class AIConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversation
        fields = '__all__'


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = '__all__'


class AIToolCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIToolCall
        fields = '__all__'
