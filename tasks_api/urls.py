"""
URL routing for the tasks application.

Defines the URL patterns for task-related views, mapping HTTP requests 
to the appropriate viewsets and ensuring correct access to task resources.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import TasksViewSet

router = DefaultRouter()
router.register(r'tasks', TasksViewSet, basename='task')

urlpatterns = router.urls
urlpatterns = [
    path('', include(router.urls)),
]
