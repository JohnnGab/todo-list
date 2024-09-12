"""
Models for the tasks application.

This module defines the database models used for task management in the To-Do List application.
These models are used to manage task-related data, including task descriptions, status, priority, 
and deadlines.

The models interact with Django's ORM and are essential for handling tasks such as
creating, updating, retrieving, and deleting tasks
"""
from django.db import models
from django.conf import settings

class Task(models.Model):
    """
    Task model for the tasks_api application.

    This model represents a task in the To-Do List application. It stores information 
    about the task's title, description, status, and the user to whom the task is assigned. 
    The status of each task is represented by predefined choices such as 'New', 'In Progress', 
    and 'Completed'.

    Attributes:
        title (CharField): The title of the task, required, maximum length of 255 characters.
        description (TextField): A detailed description of the task, optional and can be left blank.
        status (CharField): The current status of the task, chosen from predefined options 
            ('New', 'In Progress', 'Completed'). Defaults to 'New'.
        user (ForeignKey): The user who is assigned to the task, linked to the custom user model.

    Methods:
        __str__(): Returns the string representation of the task, which is its title.
    """
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}'
