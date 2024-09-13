"""
Serializers for the application's API.

This module defines the serializers used to convert model instances to JSON 
and validate data for creating or updating models. It extends and customizes 
Django Rest Framework (DRF) serializers to handle various models within the 
application, ensuring proper validation, serialization, and deserialization 
of data.
"""
from rest_framework import serializers
from .models import Task

class TasksSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.

    This serializer handles the conversion of Task model instances to and from
    JSON representations. It includes all fields from the Task model and ensures that
    the 'user' field is read-only.

    Methods:
        create(validated_data): Overrides the create method to automatically assign the
        task to the currently authenticated user.
    """
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        """
        Override the create method to assign the task to the authenticated user.
        """
        print(validated_data)
        # Assign the user from the request context to the new task
        user = self.context['request'].user
        task = Task.objects.create(user=user, **validated_data)
        return task
