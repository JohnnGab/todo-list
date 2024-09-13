"""
Custom permissions for the tasks application.

This module defines custom permissions used in the To-Do List application to control 
access to task objects. The permissions ensure that only the owner of a task can 
modify it, while other users have read-only access.
from rest_framework import permissions
"""
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a task to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the task
        return obj.user == request.user
