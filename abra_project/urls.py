from django.contrib import admin
from django.urls import path
from .views import MessageList, UnreadMessages, MessageDetail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('messages/', MessageList.as_view(), name='message-list'),  # For posting a new message
    path('messages/unread/', UnreadMessages.as_view(), name='unread-messages'),  # Existing, for unread messages
    path('message/<int:pk>/', MessageDetail.as_view(), name='message-detail'),  # Existing, for specific message operations
    
]
