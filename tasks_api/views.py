"""
Views for the tasks_api application.

This module contains views related to task management in the To-Do List application.
The views are built using Django REST Framework (DRF).
The views are intended to handle HTTP requests and provide appropriate responses.
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from .models import Task
from .permissions import IsOwnerOrReadOnly
from .serializers import TasksSerializer

class TasksViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.

    Provides CRUD operations for tasks, allowing:
        - Admin users to access all tasks.
        - Regular users to access, create, update, and delete their own tasks.
    """
    serializer_class = TasksSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        """
        If the user is an admin, return all tasks.
        Otherwise, return only the tasks assigned to the authenticated user.
        """
        if self.request.user.is_staff:
            return Task.objects.all().order_by('title')
        # Non-admin users can only see their own tasks
        return Task.objects.filter(user=self.request.user).order_by('title')
