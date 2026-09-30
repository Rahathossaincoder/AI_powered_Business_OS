from django.contrib import admin

from .models import AIConversation, AIMessage, AIToolCall


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('conversation_id', 'organization', 'user', 'title', 'model_name', 'status', 'updated_at')
    search_fields = ('title', 'user__email', 'organization__name')
    list_filter = ('organization', 'status')


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'conversation', 'role', 'sequence_number', 'created_at')
    search_fields = ('content', 'conversation__title')
    list_filter = ('role', 'conversation__organization')


@admin.register(AIToolCall)
class AIToolCallAdmin(admin.ModelAdmin):
    list_display = ('tool_call_id', 'conversation', 'tool_name', 'status', 'execution_time_ms', 'created_at')
    search_fields = ('tool_name', 'conversation__title')
    list_filter = ('status', 'conversation__organization')
