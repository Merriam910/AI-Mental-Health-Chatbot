from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings  # for settings.AUTH_USER_MODEL


# --- Custom User ---
class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    pass


# --- Conversation Model ---
class Conversation(models.Model):
    conversation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Conversation {self.conversation_id} - User {self.user.username}"


# --- Session Model ---
class Session(models.Model):
    session_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    conversation = models.ForeignKey(Conversation, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Session {self.session_id} - User {self.user.username}"

    def has_conversation(self):
        return self.conversation is not None

    def has_user_messages(self):
        if self.conversation:
            return self.conversation.messages.filter(sender='user').exists()
        return False


# --- Message Model ---
class Message(models.Model):
    MESSAGE_SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    message_id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=MESSAGE_SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[{self.timestamp}] {self.sender}: {self.content[:50]}"


# --- Feedback Model ---
class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} for session {self.session.session_id}"

    def is_allowed(self):
        return (
            self.session and
            self.session.conversation is not None and
            self.session.conversation.messages.filter(sender='user').exists()
        )
class Report(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    report_id = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_id} - {self.email}"