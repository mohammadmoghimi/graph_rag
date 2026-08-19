from django.contrib import admin

from .models import ChatSession, ChatSessionWebsite, ChatMessage


admin.site.register(ChatSession)
admin.site.register(ChatSessionWebsite)
admin.site.register(ChatMessage)