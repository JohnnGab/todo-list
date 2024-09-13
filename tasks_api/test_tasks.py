# pylint: disable=W0621
"""
Unit tests for the tasks application.

These tests ensure the correctness of the task management functionality, 
including model validation and API behavior. The tests cover various operations 
such as task creation, retrieval, updating, and deletion, as well as permission 
handling to ensure only authorized users can modify their tasks.

Note:
- Pytest is used for running the tests.
- The APIClient from Django REST Framework is used to simulate HTTP requests 
  to the tasks API.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()

@pytest.fixture
def api_client():
    """Returns an instance of APIClient for making API requests in tests."""
    return APIClient()


@pytest.mark.django_db
def test_create_task(api_client):
    """
    Test creating a task using a valid JWT token.
    """
    # Create a user and get tokens
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'last_name' : 'Dillinger',
        'password': 'password123!@#',
        'email': 'testuser@example.com',
    }

    registration_response = api_client.post(url, data, format='json')
    assert registration_response.status_code == status.HTTP_201_CREATED

    # Login with the user
    login_data = {'username': 'testuser', 'password': 'password123!@#'}
    login_response = api_client.post('/auth/jwt/create/', login_data, format='json')

    access_token = login_response.data['access']
    assert access_token is not None, "No access token returned"

    # Set the Authorization header with the token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Create a task
    task_data = {
        'title': 'Test Task',
        'description': 'This is a test task',
        'status': 'New'
    }

    task_create_response = api_client.post('/api/tasks/', task_data, format='json')
    print(task_create_response.data)
    # Access a protected view (e.g., user details)
    assert task_create_response.status_code == status.HTTP_201_CREATED
    assert task_create_response.data['title'] == 'Test Task'
    assert task_create_response.data['description'] == 'This is a test task'
    assert task_create_response.data['status'] == 'New'


@pytest.mark.django_db
def test_list_user_tasks(api_client):
    """
    Test listing tasks for each user. One user should have a task, and the other should have none.
    """
    # Create two users
    url = '/auth/users/'
    user1_data = {
        'username': 'testuser1',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'password123!@#',
        'email': 'testuser1@example.com',
    }
    user2_data = {
        'username': 'testuser2',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'password': 'password123!@#',
        'email': 'testuser2@example.com',
    }

    # Register user1
    registration_response1 = api_client.post(url, user1_data, format='json')
    assert registration_response1.status_code == status.HTTP_201_CREATED

    # Register user2
    registration_response2 = api_client.post(url, user2_data, format='json')
    assert registration_response2.status_code == status.HTTP_201_CREATED

    # Login as user1
    login_data1 = {'username': 'testuser1', 'password': 'password123!@#'}
    login_response1 = api_client.post('/auth/jwt/create/', login_data1, format='json')
    access_token1 = login_response1.data['access']
    assert access_token1 is not None, "No access token returned for user1"

    # Set the Authorization header with the token for user1
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token1}')

    # Create a task assigned to user1
    task_data = {
        'title': 'Test Task',
        'description': 'This is a test task',
        'status': 'New'
    }
    task_create_response = api_client.post('/api/tasks/', task_data, format='json')
    assert task_create_response.status_code == status.HTTP_201_CREATED
    assert task_create_response.data['title'] == 'Test Task'
    assert task_create_response.data['description'] == 'This is a test task'
    assert task_create_response.data['status'] == 'New'

    # List tasks for user1
    tasks_response1 = api_client.get('/api/tasks/', format='json')
    assert tasks_response1.status_code == status.HTTP_200_OK
    assert len(tasks_response1.data['results']) == 1, "User1 should have one task"
    assert tasks_response1.data['results'][0]['title'] == 'Test Task'

    # Reset credentials
    api_client.credentials()

    # Login as user2
    login_data2 = {'username': 'testuser2', 'password': 'password123!@#'}
    login_response2 = api_client.post('/auth/jwt/create/', login_data2, format='json')
    access_token2 = login_response2.data['access']
    assert access_token2 is not None, "No access token returned for user2"

    # Set the Authorization header with the token for user2
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token2}')

    # List tasks for user2
    tasks_response2 = api_client.get('/api/tasks/', format='json')
    assert tasks_response2.status_code == status.HTTP_200_OK
    assert len(tasks_response2.data['results']) == 0, "User2 should have no tasks"


def test_admin_can_list_all_tasks(api_client, django_user_model):
    """
    Test that admin user can list all tasks.
    """
    # Create a regular user
    url = '/auth/users/'
    user1_data = {
        'username': 'testuser1',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'password123!@#',
        'email': 'testuser1@example.com',
    }

    # Register user1
    registration_response1 = api_client.post(url, user1_data, format='json')
    assert registration_response1.status_code == status.HTTP_201_CREATED

    # Login as user1
    login_data1 = {'username': 'testuser1', 'password': 'password123!@#'}
    login_response1 = api_client.post('/auth/jwt/create/', login_data1, format='json')
    assert login_response1.status_code == status.HTTP_200_OK, "User1 login failed"
    access_token1 = login_response1.data['access']
    assert access_token1 is not None, "No access token returned for user1"

    # Set the Authorization header with the token for user1
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token1}')

    # Create a task assigned to user1
    task_data = {
        'title': 'Test Task',
        'description': 'This is a test task',
        'status': 'New'
    }
    task_create_response = api_client.post('/api/tasks/', task_data, format='json')
    assert task_create_response.status_code == status.HTTP_201_CREATED
    assert task_create_response.data['title'] == 'Test Task'
    assert task_create_response.data['description'] == 'This is a test task'
    assert task_create_response.data['status'] == 'New'

    # Reset credentials
    api_client.credentials()

    # Create admin user (if not already created)
    admin_username = 'admin'
    admin_password = 'Admin123@'

    # Check if admin user exists; if not, create one
    if not django_user_model.objects.filter(username=admin_username).exists():
        django_user_model.objects.create_superuser(
            username=admin_username,
            email='admin@example.com',
            password=admin_password
        )

    # Login as admin
    login_data_admin = {'username': admin_username, 'password': admin_password}
    login_response_admin = api_client.post('/auth/jwt/create/', login_data_admin, format='json')
    assert login_response_admin.status_code == status.HTTP_200_OK, "Admin login failed"
    access_token_admin = login_response_admin.data['access']
    assert access_token_admin is not None, "No access token returned for admin"

    # Set the Authorization header with the token for admin
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token_admin}')

    # List tasks as admin
    tasks_response_admin = api_client.get('/api/tasks/', format='json')
    assert tasks_response_admin.status_code == status.HTTP_200_OK, "Admin failed to retrieve tasks"
    # Verify that admin can see the task created by user1
    assert len(tasks_response_admin.data['results']) == 1, "Admin should see all tasks"
    assert tasks_response_admin.data['results'][0]['title'] == 'Test Task'


@pytest.mark.django_db
def test_get_specific_task(api_client):
    """
    Test getting information about a specific task.
    """
    # Create a user and get tokens
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'last_name': 'Dillinger',
        'password': 'password123!@#',
        'email': 'testuser@example.com',
    }

    registration_response = api_client.post(url, data, format='json')
    assert registration_response.status_code == status.HTTP_201_CREATED, "User registration failed"

    # Login with the user
    login_data = {'username': 'testuser', 'password': 'password123!@#'}
    login_response = api_client.post('/auth/jwt/create/', login_data, format='json')
    assert login_response.status_code == status.HTTP_200_OK, "User login failed"

    access_token = login_response.data.get('access')
    assert access_token is not None, "No access token returned"

    # Set the Authorization header with the token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Create a task
    task_data = {
        'title': 'Test Task',
        'description': 'This is a test task',
        'status': 'New'
    }

    task_create_response = api_client.post('/api/tasks/', task_data, format='json')
    assert task_create_response.status_code == status.HTTP_201_CREATED, "Task creation failed"
    assert task_create_response.data['title'] == 'Test Task', "Task title mismatch"
    assert (task_create_response.data['description'] == 'This is a test task'
    ),"Task description mismatch"
    assert task_create_response.data['status'] == 'New', "Task status mismatch"

    # Get the ID of the created task
    task_id = task_create_response.data['id']

    # Retrieve the specific task
    task_detail_url = f'/api/tasks/{task_id}/'
    task_detail_response = api_client.get(task_detail_url, format='json')
    assert (task_detail_response.status_code == status.HTTP_200_OK
    ), f"Failed to retrieve task {task_id}"
    assert task_detail_response.data['id'] == task_id, "Task ID mismatch"
    assert task_detail_response.data['title'] == 'Test Task', "Task title mismatch"
    assert (task_detail_response.data['description'] == 'This is a test task'
    ), "Task description mismatch"
    assert task_detail_response.data['status'] == 'New', "Task status mismatch"


@pytest.mark.django_db
def test_owner_can_update_task(api_client):
    """
    Test that the task owner can fully update task information.
    """
    # Create a user and get tokens
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'last_name': 'Dillinger',
        'password': 'password123!@#',
        'email': 'testuser@example.com',
    }

    registration_response = api_client.post(url, data, format='json')
    assert registration_response.status_code == status.HTTP_201_CREATED, "User registration failed"

    # Login with the user
    login_data = {'username': 'testuser', 'password': 'password123!@#'}
    login_response = api_client.post('/auth/jwt/create/', login_data, format='json')
    assert login_response.status_code == status.HTTP_200_OK, "User login failed"

    access_token = login_response.data.get('access')
    assert access_token is not None, "No access token returned"

    # Set the Authorization header with the token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Create a task
    task_data = {
        'title': 'Test Task',
        'description': 'This is a test task',
        'status': 'New'
    }

    task_create_response = api_client.post('/api/tasks/', task_data, format='json')
    assert task_create_response.status_code == status.HTTP_201_CREATED, "Task creation failed"
    assert task_create_response.data['title'] == 'Test Task'
    assert task_create_response.data['description'] == 'This is a test task'
    assert task_create_response.data['status'] == 'New'

    # Get the ID of the created task
    task_id = task_create_response.data['id']

    # Update the task
    updated_task_data = {
        'title': 'Updated Task',
        'description': 'This is an updated test task',
        'status': 'In Progress'
    }

    task_update_response = api_client.put(
        f'/api/tasks/{task_id}/',
        updated_task_data,
        format='json'
    )
    assert task_update_response.status_code == status.HTTP_200_OK, "Task update failed"
    assert task_update_response.data['title'] == 'Updated Task'
    assert task_update_response.data['description'] == 'This is an updated test task'
    assert task_update_response.data['status'] == 'In Progress'

    # Verify that the task was updated
    task_detail_response = api_client.get(f'/api/tasks/{task_id}/', format='json')
    assert task_detail_response.status_code == status.HTTP_200_OK, "Failed to retrieve task"
    assert task_detail_response.data['title'] == 'Updated Task'
    assert task_detail_response.data['description'] == 'This is an updated test task'
    assert task_detail_response.data['status'] == 'In Progress'


@pytest.mark.django_db
def test_user_cannot_update_unowned_task(api_client):
    """
    Test that a user cannot update a task they do not own.
    """
    # Create user1 and get tokens
    url = '/auth/users/'
    user1_data = {
        'username': 'user1',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'password123!@#',
        'email': 'user1@example.com',
    }

    registration_response1 = api_client.post(url, user1_data, format='json')
    assert (registration_response1.status_code == status.HTTP_201_CREATED
    ), "User1 registration failed"

    # Login with user1
    login_data1 = {'username': 'user1', 'password': 'password123!@#'}
    login_response1 = api_client.post('/auth/jwt/create/', login_data1, format='json')
    assert login_response1.status_code == status.HTTP_200_OK, "User1 login failed"

    access_token1 = login_response1.data.get('access')
    assert access_token1 is not None, "No access token returned for user1"

    # Set the Authorization header with the token for user1
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token1}')

    # Create a task as user1
    task_data = {
        'title': 'User1 Task',
        'description': 'Task created by user1',
        'status': 'New'
    }

    task_create_response = api_client.post('/api/tasks/', task_data, format='json')
    assert task_create_response.status_code == status.HTTP_201_CREATED, "Task creation failed"
    task_id = task_create_response.data['id']

    # Reset credentials
    api_client.credentials()

    # Create user2
    user2_data = {
        'username': 'user2',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'password': 'password123!@#',
        'email': 'user2@example.com',
    }

    registration_response2 = api_client.post(url, user2_data, format='json')
    assert (registration_response2.status_code == status.HTTP_201_CREATED
    ), "User2 registration failed"

    # Login with user2
    login_data2 = {'username': 'user2', 'password': 'password123!@#'}
    login_response2 = api_client.post('/auth/jwt/create/', login_data2, format='json')
    assert login_response2.status_code == status.HTTP_200_OK, "User2 login failed"

    access_token2 = login_response2.data.get('access')
    assert access_token2 is not None, "No access token returned for user2"

    # Set the Authorization header with the token for user2
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token2}')

    # Attempt to update user1's task as user2
    updated_task_data = {
        'title': 'Updated Task by User2',
        'description': 'User2 attempting to update task',
        'status': 'In Progress'
    }

    task_update_response = api_client.put(
        f'/api/tasks/{task_id}/',
        updated_task_data,
        format='json'
    )

    # Expected behavior: user2 should not be able to update user1's task
    assert (task_update_response.status_code == status.HTTP_404_NOT_FOUND
            ), "User2 should not be able to update user1's task"


@pytest.mark.django_db
def test_delete_task_only_by_owner(api_client):
    """
    Test that a task can be deleted only by its owner.
    """
    # Create user1 and get tokens
    url = '/auth/users/'
    user1_data = {
        'username': 'user1',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'password123!@#',
        'email': 'user1@example.com',
    }

    registration_response1 = api_client.post(url, user1_data, format='json')
    assert (registration_response1.status_code == status.HTTP_201_CREATED
    ), "User1 registration failed"

    # Login with user1
    login_data1 = {'username': 'user1', 'password': 'password123!@#'}
    login_response1 = api_client.post('/auth/jwt/create/', login_data1, format='json')
    assert login_response1.status_code == status.HTTP_200_OK, "User1 login failed"

    access_token1 = login_response1.data.get('access')
    assert access_token1 is not None, "No access token returned for user1"

    # Set the Authorization header with the token for user1
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token1}')

    # Create a task as user1
    task_data = {
        'title': 'User1 Task',
        'description': 'Task created by user1',
        'status': 'New'
    }

    task_create_response = api_client.post('/api/tasks/', task_data, format='json')
    assert task_create_response.status_code == status.HTTP_201_CREATED, "Task creation failed"
    task_id = task_create_response.data['id']

    # Attempt to delete the task as user1 (should succeed)
    task_delete_url = f'/api/tasks/{task_id}/'
    task_delete_response = api_client.delete(task_delete_url)
    assert (task_delete_response.status_code == status.HTTP_204_NO_CONTENT
    ), "User1 should be able to delete their own task"

    # Verify the task is deleted by trying to get it (should return 404)
    task_get_response = api_client.get(task_delete_url)
    assert (task_get_response.status_code == status.HTTP_404_NOT_FOUND
    ), "Deleted task should not be retrievable"

    # Create user2 and get tokens
    user2_data = {
        'username': 'user2',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'password': 'password123!@#',
        'email': 'user2@example.com',
    }

    registration_response2 = api_client.post(url, user2_data, format='json')
    assert (registration_response2.status_code == status.HTTP_201_CREATED
    ), "User2 registration failed"

    # Login with user2
    login_data2 = {'username': 'user2', 'password': 'password123!@#'}
    login_response2 = api_client.post('/auth/jwt/create/', login_data2, format='json')
    assert login_response2.status_code == status.HTTP_200_OK, "User2 login failed"

    access_token2 = login_response2.data.get('access')
    assert access_token2 is not None, "No access token returned for user2"

    # Set the Authorization header with the token for user2
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token2}')

    # Attempt to delete the task as user2 (should fail)
    task_delete_response = api_client.delete(task_delete_url)
    assert (task_delete_response.status_code in
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    ), ("User2 should not be able to delete user1's task")


@pytest.mark.django_db
def test_mark_task_as_completed(api_client):
    """
    Test that the task owner can mark a task as completed.
    """
    # Create a user and get tokens
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'last_name': 'Dillinger',
        'password': 'password123!@#',
        'email': 'testuser@example.com',
    }

    registration_response = api_client.post(url, data, format='json')
    assert registration_response.status_code == status.HTTP_201_CREATED, "User registration failed"

    # Login with the user
    login_data = {'username': 'testuser', 'password': 'password123!@#'}
    login_response = api_client.post('/auth/jwt/create/', login_data, format='json')
    assert login_response.status_code == status.HTTP_200_OK, "User login failed"

    access_token = login_response.data.get('access')
    assert access_token is not None, "No access token returned"

    # Set the Authorization header with the token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Create a task with status 'New'
    task_data = {
        'title': 'Test Task',
        'description': 'This is a test task',
        'status': 'New'
    }

    task_create_response = api_client.post('/api/tasks/', task_data, format='json')
    assert task_create_response.status_code == status.HTTP_201_CREATED, "Task creation failed"
    assert task_create_response.data['title'] == 'Test Task'
    assert task_create_response.data['description'] == 'This is a test task'
    assert task_create_response.data['status'] == 'New'

    # Get the ID of the created task
    task_id = task_create_response.data['id']

    # Update the task's status to 'Completed'
    updated_task_data = {
        'status': 'Completed'
    }

    task_update_response = api_client.patch(
        f'/api/tasks/{task_id}/',
        updated_task_data,
        format='json'
    )
    assert task_update_response.status_code == status.HTTP_200_OK, "Task status update failed"
    assert (task_update_response.data['status'] == 'Completed'
    ), "Task status was not updated to 'Completed'"

    # Verify that the task's status was updated
    task_detail_response = api_client.get(f'/api/tasks/{task_id}/', format='json')
    assert task_detail_response.status_code == status.HTTP_200_OK, "Failed to retrieve task"
    assert task_detail_response.data['status'] == 'Completed', "Task status mismatch after update"

    # Optionally, attempt to mark the task as completed by another user (should fail)
    # Create another user
    user2_data = {
        'username': 'user2',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'password': 'password123!@#',
        'email': 'user2@example.com',
    }

    registration_response2 = api_client.post(url, user2_data, format='json')
    assert (registration_response2.status_code == status.HTTP_201_CREATED
    ), "User2 registration failed"

    # Login with user2
    login_data2 = {'username': 'user2', 'password': 'password123!@#'}
    login_response2 = api_client.post('/auth/jwt/create/', login_data2, format='json')
    assert login_response2.status_code == status.HTTP_200_OK, "User2 login failed"

    access_token2 = login_response2.data.get('access')
    assert access_token2 is not None, "No access token returned for user2"

    # Set the Authorization header with the token for user2
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token2}')

    # Attempt to update the task's status as user2
    updated_task_data_user2 = {
        'status': 'Completed'
    }

    task_update_response_user2 = api_client.patch(
        f'/api/tasks/{task_id}/',
        updated_task_data_user2,
        format='json'
    )

    # Expected behavior: user2 should not be able to update user1's task
    assert (task_update_response_user2.status_code
    in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]), (
        "User2 should not be able to mark user1's task as completed"
    )


@pytest.mark.django_db
def test_filter_tasks_by_status(api_client):
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
    assert (task_create_response_new.status_code == status.HTTP_201_CREATED
    ), "Task creation failed for status 'New'"

    # Create the second task with status 'Completed'
    task_data_completed = {
        'title': 'Task Completed',
        'description': 'This is a completed task',
        'status': 'Completed'
    }
    task_create_response_completed = api_client.post(
        '/api/tasks/',
        task_data_completed,
        format='json'
    )
    assert (task_create_response_completed.status_code == status.HTTP_201_CREATED
    ), "Task creation failed for status 'Completed'"

    # Filter tasks by status 'New'
    filter_status = 'New'
    task_list_response_new = api_client.get(f'/api/tasks/?status={filter_status}', format='json')
    assert (task_list_response_new.status_code == status.HTTP_200_OK
    ), "Failed to retrieve tasks with status 'New'"

    tasks_new = task_list_response_new.data['results']
    assert len(tasks_new) == 1, f"Expected 1 task with status 'New', got {len(tasks_new)}"
    assert (tasks_new[0]['status'] == 'New'
    ), f"Task status mismatch: expected 'New', got {tasks_new[0]['status']}"
    assert tasks_new[0]['title'] == 'Task New', "Task title mismatch for status 'New'"

    # Filter tasks by status 'Completed'
    filter_status = 'Completed'
    task_list_response_completed = api_client.get(
        f'/api/tasks/?status={filter_status}',
        format='json'
    )
    assert (task_list_response_completed.status_code == status.HTTP_200_OK
    ), "Failed to retrieve tasks with status 'Completed'"

    tasks_completed = task_list_response_completed.data['results']
    assert (len(tasks_completed) == 1
    ), f"Expected 1 task with status 'Completed', got {len(tasks_completed)}"
    assert (tasks_completed[0]['status'] == 'Completed'
    ), f"Task status mismatch: expected 'Completed', got {tasks_completed[0]['status']}"
    assert (tasks_completed[0]['title'] == 'Task Completed'
    ), "Task title mismatch for status 'Completed'"

    # Optionally, test filtering with a status that has no tasks
    filter_status = 'In Progress'
    task_list_response_none = api_client.get(f'/api/tasks/?status={filter_status}', format='json')
    assert task_list_response_none.status_code == status.HTTP_200_OK, "Failed to retrieve tasks"
    tasks_none = task_list_response_none.data['results']
    assert (len(tasks_none) == 0
    ), f"Expected 0 tasks with status '{filter_status}', got {len(tasks_none)}"
