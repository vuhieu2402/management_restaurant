from django.contrib import admin
from .models import Conversation, Message, RecommendedDish, UserPreference

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['created_at']

class RecommendedDishInline(admin.TabularInline):
    model = RecommendedDish
    extra = 0
    readonly_fields = ['created_at']

class UserPreferenceInline(admin.TabularInline):
    model = UserPreference
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'created_at', 'updated_at']
    search_fields = ['session_id', 'user__email']
    list_filter = ['created_at', 'updated_at']
    inlines = [MessageInline, RecommendedDishInline, UserPreferenceInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'short_content', 'created_at']
    list_filter = ['sender', 'created_at']
    search_fields = ['content', 'conversation__session_id']
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'

@admin.register(RecommendedDish)
class RecommendedDishAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'dish', 'is_accepted', 'created_at']
    list_filter = ['is_accepted', 'created_at']
    search_fields = ['dish__name', 'conversation__session_id']

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'preference_type', 'preference_value', 'confidence', 'created_at']
    list_filter = ['preference_type', 'created_at']
    search_fields = ['preference_value', 'user__email']
