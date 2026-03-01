from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    owner_id = serializers.ReadOnlyField(source='owner.id')
    
    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'completed',
            'created_at',
            'updated_at',
            'owner',
            'owner_id'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'owner', 'owner_id')
    
    def validate_title(self, value):
        """Validate that title is not empty after stripping whitespace"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty or whitespace only.")
        return value


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tasks
    """
    
    class Meta:
        model = Task
        fields = ('title', 'description', 'completed')
    
    def validate_title(self, value):
        """Validate that title is not empty after stripping whitespace"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty or whitespace only.")
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating tasks
    """
    
    class Meta:
        model = Task
        fields = ('title', 'description', 'completed')
    
    def validate_title(self, value):
        """Validate that title is not empty after stripping whitespace"""
        if value and not value.strip():
            raise serializers.ValidationError("Title cannot be empty or whitespace only.")
        return value

