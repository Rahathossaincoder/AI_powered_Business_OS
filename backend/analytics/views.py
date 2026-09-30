from rest_framework import viewsets

from .models import AIConversation, AIMessage, AIToolCall
from .serializers import AIConversationSerializer, AIMessageSerializer, AIToolCallSerializer


class AIConversationViewSet(viewsets.ModelViewSet):
    queryset = AIConversation.objects.all()
    serializer_class = AIConversationSerializer


class AIMessageViewSet(viewsets.ModelViewSet):
    queryset = AIMessage.objects.all()
    serializer_class = AIMessageSerializer


class AIToolCallViewSet(viewsets.ModelViewSet):
    queryset = AIToolCall.objects.all()
    serializer_class = AIToolCallSerializer
