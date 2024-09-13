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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New', db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}'

import pytest
from rest_framework import status

@pytest.mark.django_db
def test_filter_tasks_by_status_simple(api_client):
    """
    Test filtering tasks by status with two tasks of different statuses.
    """
    # Create a user and get tokens
    url = '/auth/users/'
    user_data = {
        'username': 'testuser',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'password123!@#',
        'email': 'testuser@example.com',
    }

    registration_response = api_client.post(url, user_data, format='json')
    assert registration_response.status_code == status.HTTP_201_CREATED, "User registration failed"

    # Login with the user
    login_data = {'username': 'testuser', 'password': 'password123!@#'}
    login_response = api_client.post('/auth/jwt/create/', login_data, format='json')
    assert login_response.status_code == status.HTTP_200_OK, "User login failed"

    access_token = login_response.data.get('access')
    assert access_token is not None, "No access token returned"

    # Set the Authorization header with the token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Create the first task with status 'New'
    task_data_new = {
        'title': 'Task New',
        'description': 'This is a new task',
        'status': 'New'
    }
    task_create_response_new = api_client.post('/api/tasks/', task_data_new, format='json')
    assert task_create_response_new.status_code == status.HTTP_201_CREATED, "Task creation failed for status 'New'"

    # Create the second task with status 'Completed'
    task_data_completed = {
        'title': 'Task Completed',
        'description': 'This is a completed task',
        'status': 'Completed'
    }
    task_create_response_completed = api_client.post('/api/tasks/', task_data_completed, format='json')
    assert task_create_response_completed.status_code == status.HTTP_201_CREATED, "Task creation failed for status 'Completed'"

    # Filter tasks by status 'New'
    filter_status = 'New'
    task_list_response_new = api_client.get(f'/api/tasks/?status={filter_status}', format='json')
    assert task_list_response_new.status_code == status.HTTP_200_OK, "Failed to retrieve tasks with status 'New'"

    tasks_new = task_list_response_new.data
    assert len(tasks_new) == 1, f"Expected 1 task with status 'New', got {len(tasks_new)}"
    assert tasks_new[0]['status'] == 'New', f"Task status mismatch: expected 'New', got {tasks_new[0]['status']}"
    assert tasks_new[0]['title'] == 'Task New', "Task title mismatch for status 'New'"

    # Filter tasks by status 'Completed'
    filter_status = 'Completed'
    task_list_response_completed = api_client.get(f'/api/tasks/?status={filter_status}', format='json')
    assert task_list_response_completed.status_code == status.HTTP_200_OK, "Failed to retrieve tasks with status 'Completed'"

    tasks_completed = task_list_response_completed.data
    assert len(tasks_completed) == 1, f"Expected 1 task with status 'Completed', got {len(tasks_completed)}"
    assert tasks_completed[0]['status'] == 'Completed', f"Task status mismatch: expected 'Completed', got {tasks_completed[0]['status']}"
    assert tasks_completed[0]['title'] == 'Task Completed', "Task title mismatch for status 'Completed'"

    # Optionally, test filtering with a status that has no tasks
    filter_status = 'In Progress'
    task_list_response_none = api_client.get(f'/api/tasks/?status={filter_status}', format='json')
    assert task_list_response_none.status_code == status.HTTP_200_OK, "Failed to retrieve tasks"
    tasks_none = task_list_response_none.data
    assert len(tasks_none) == 0, f"Expected 0 tasks with status '{filter_status}', got {len(tasks_none)}"
