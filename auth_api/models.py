"""
Models for the auth_api application.

This module defines the database models used for authentication and authorization 
in the To-Do List application. These models are used to manage user data, including
credentials, permissions, and any other information related to user authentication.

The models interact with Django's ORM and are essential for handling tasks such as 
user registration, login, and managing access control.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model for the auth_api application.

    This model extends the default Django user model to support additional fields
    or functionalities required for the authentication system. It stores user credentials
    and any other information relevant to authentication and authorization, such as 
    email, username, and password.

    Attributes:
        username (CharField): The unique identifier for the user.
        email (EmailField): The user's email address.
        password (CharField): The user's hashed password.
        is_active (BooleanField): Indicates whether the user's account is active.
    """
    first_name = models.CharField(max_length=150, blank=False, null=False)

    def __str__(self):
        return f'{self.username}'
