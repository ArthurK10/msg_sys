from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Message
from .serializers import MessageSerializer
from django.shortcuts import get_object_or_404

class MessageList(APIView):
    """
    List all messages for a specific user or create a new message.
    """
    authentication_classes = [TokenAuthentication]  # Enforce Token Authentication
    permission_classes = [IsAuthenticated]  # Allow access to authenticated users only

    def get(self, request, user_id=None, format=None):
        # Only allow users to fetch their own messages, regardless of the user_id passed in the URL.
        user = request.user
        
        # This checks for messages where the authenticated user is the receiver.
        messages = Message.objects.filter(receiver=request.user).order_by('-creation_date')
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # Copy the request data to make it mutable
        data = request.data.copy()

        # Explicitly set the 'sender' using the authenticated user's ID
        # and ensure 'receiver_id' is obtained from the request body.
        data['sender'] = request.user.id
        # Initialize your serializer with the updated data
        serializer = MessageSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnreadMessages(APIView):
    """
    List all unread messages for a specific user.
    """
    authentication_classes = [TokenAuthentication]  # Enforce Token Authentication
    permission_classes = [IsAuthenticated] 

    def get(self, request, format=None):
        unread_messages = Message.objects.filter(receiver=request.user, is_read=False)
        serializer = MessageSerializer(unread_messages, many=True)
        return Response(serializer.data)



class MessageDetail(APIView):
    """
    Retrieve, update or delete a message instance.
    """
    authentication_classes = [TokenAuthentication]  # Enforce Token Authentication
    permission_classes = [IsAuthenticated] 


    def get(self, request, pk, format=None):
        # Fetch the message, ensuring it exists
        message = get_object_or_404(Message, pk=pk)

        # Check if the request.user is the receiver of the message
        if message.receiver != request.user:
            return Response({"detail": "Not authorized to view this message."}, status=403)

        # Mark the message as read
        if not message.is_read:
            message.is_read = True
            message.save(update_fields=['is_read'])

        # Serialize and return the message
        serializer = MessageSerializer(message)
        return Response(serializer.data)


    def delete(self, request, pk, format=None):
        message = get_object_or_404(Message, pk=pk)
        # Check if the request.user is the receiver of the message
        if message.receiver == request.user:
            message.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # If the user is not authorized to delete the message, return a 403 Forbidden response
            return Response({"detail": "Not authorized to delete this message."}, status=status.HTTP_403_FORBIDDEN)