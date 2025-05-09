from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, Session, Message, Feedback, Report

# --- Custom User Admin ---
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'username', 'email', 'first_name', 'get_hashed_password', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    def get_hashed_password(self, obj):
        return obj.password
    get_hashed_password.short_description = 'Password'

admin.site.register(User, CustomUserAdmin)

# --- Custom Conversation Admin ---
class ConversationAdmin(admin.ModelAdmin):
    model = Conversation
    list_display = ('conversation_id', 'get_user_id', 'start_time', 'end_time')
    search_fields = ('user__username', 'user__email')
    list_filter = ('start_time', 'user__email')

    @admin.display(description='User ID')
    def get_user_id(self, obj):
        return obj.user.id

admin.site.register(Conversation, ConversationAdmin)

# --- Custom Session Admin ---
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'get_user_id', 'start_time', 'end_time', 'get_conversation_id']
    list_filter = ['user', 'start_time', 'end_time']
    search_fields = ['user__username', 'user__email']

    @admin.display(description='User ID')
    def get_user_id(self, obj):
        return obj.user.id

    @admin.display(description='Conversation ID')
    def get_conversation_id(self, obj):
        return obj.conversation.conversation_id if obj.conversation else None

admin.site.register(Session, SessionAdmin)

# --- Custom Message Admin ---
class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = ('message_id', 'get_conversation_id', 'get_user_id', 'sender', 'content', 'timestamp')
    list_filter = ('sender', 'timestamp', 'conversation')
    search_fields = ('content', 'conversation__user__username', 'conversation__user__email')

    @admin.display(description='Conversation ID')
    def get_conversation_id(self, obj):
        return obj.conversation.conversation_id

    @admin.display(description='User ID')
    def get_user_id(self, obj):
        return obj.conversation.user.id

admin.site.register(Message, MessageAdmin)

# --- Custom Feedback Admin ---
class FeedbackAdmin(admin.ModelAdmin):
    model = Feedback
    list_display = ('feedback_id', 'get_user_id', 'get_session_id', 'content', 'timestamp')
    list_filter = ('user', 'session', 'timestamp')
    search_fields = ('content', 'user__username', 'user__email', 'session__session_id')

    @admin.display(description='User ID')
    def get_user_id(self, obj):
        return obj.user.id

    @admin.display(description='Session ID')
    def get_session_id(self, obj):
        return obj.session.session_id

admin.site.register(Feedback, FeedbackAdmin)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'report_id', 'created_at', 'message')  # Include report_id in the list view
    search_fields = ('name', 'email', 'message', 'report_id')  # Add report_id to searchable fields
    readonly_fields = ('created_at',)  # Make sure created_at is not editable

    # Optional: Make the message field expandable and fully visible in the form
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'message', 'report_id')  # Include report_id in the form fields
        }),
        ('Additional Information', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

