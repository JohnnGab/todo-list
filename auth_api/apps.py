"""
App configuration for the tasks API.

This class configures the auth_api application within the Django project.
"""
from django.apps import AppConfig


class AuthApiConfig(AppConfig):
    """
    Configuration class for the auth_api application.

    Sets the default auto field and application name for the authentication API.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_api'
