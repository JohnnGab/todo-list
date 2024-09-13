"""
Admin configuration for managing models in the Django admin interface.

This module registers models with the Django admin site, allowing 
administrators to view, add, modify, and delete records via the admin interface.
"""
from django.contrib import admin
from .models import Task

admin.site.register(Task)
