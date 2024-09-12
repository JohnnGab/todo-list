"""
Serializers for the application's API.

This module defines the serializers used to convert model instances to JSON 
and validate data for creating or updating models. It extends and customizes 
Django Rest Framework (DRF) serializers to handle various models within the 
application, ensuring proper validation, serialization, and deserialization 
of data.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Serializer for creating a custom user with the Djoser API.

    Extends Djoser's `UserCreateSerializer` to make `first_name` required and
    'last_name' optional, text_field.

    Meta:
    model: Custom user model from `get_user_model()`.
    fields: `username`, `password`, `email`, `first_name`, `last_name`.
    """
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = UserCreateSerializer.Meta.fields  + ('first_name', 'last_name')
