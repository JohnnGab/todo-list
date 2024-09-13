"""
App configuration for the tasks API.

This class configures the tasks_api application within the Django project.
"""
from django.apps import AppConfig


class TasksApiConfig(AppConfig):
    """
    Configuration class for the tasks_api application.

    Sets the default auto field and application name for the tasks API.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks_api'
