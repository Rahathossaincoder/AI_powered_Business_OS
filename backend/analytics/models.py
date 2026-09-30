from django.db import models


class AIConversation(models.Model):
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_ARCHIVED = 'ARCHIVED'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    conversation_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='ai_conversations')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=255, blank=True)
    model_name = models.CharField(max_length=100, default='gpt-4o-mini')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_conversations'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title or f'Conversation {self.conversation_id}'


class AIMessage(models.Model):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_SYSTEM = 'system'

    ROLE_CHOICES = [
        (ROLE_USER, 'User'),
        (ROLE_ASSISTANT, 'Assistant'),
        (ROLE_SYSTEM, 'System'),
    ]

    message_id = models.BigAutoField(primary_key=True)
    conversation = models.ForeignKey('analytics.AIConversation', on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    sequence_number = models.IntegerField(default=0)
    token_count = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_messages'
        ordering = ['conversation', 'sequence_number']

    def __str__(self):
        return f'{self.role} message #{self.sequence_number}'


class AIToolCall(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    tool_call_id = models.BigAutoField(primary_key=True)
    conversation = models.ForeignKey('analytics.AIConversation', on_delete=models.CASCADE, related_name='tool_calls')
    message = models.ForeignKey('analytics.AIMessage', on_delete=models.SET_NULL, null=True, blank=True, related_name='tool_calls')
    tool_name = models.CharField(max_length=100)
    arguments = models.JSONField(default=dict)
    result = models.JSONField(default=dict, blank=True, null=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    execution_time_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ai_tool_calls'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.tool_name} ({self.status})'
