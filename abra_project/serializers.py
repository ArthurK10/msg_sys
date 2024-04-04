from rest_framework import serializers
from .models import Message
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username'] 

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)  # Keeps sender info readable but not writable
    receiver = UserSerializer(read_only=True)  # Assuming you still want receiver details in the response
    receiver_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.all(), source='receiver', label="Receiver ID")

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'receiver_id', 'subject', 'message', 'creation_date', 'is_read']
        read_only_fields = ['id', 'creation_date', 'is_read']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['sender'] = user
        return Message.objects.create(**validated_data)