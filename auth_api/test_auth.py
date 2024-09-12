# pylint: disable=W0621

"""
Unit tests for the User model and authentication system.

These tests cover:
1. User model validation:
   - Validation of required fields (first_name, username, password).
   - Optionality of last_name.
   - Uniqueness of username.
   - Password constraints (e.g., minimum length).

2. Authentication and Authorization using Djoser and JWT:
   - User registration via Djoser.
   - JWT-based login and token refresh.
   - Access to protected endpoints using valid JWT tokens.
   - Rejection of invalid login attempts.

Note:
- Pytest is used for running the tests.
- The tests interact with Django's default User model, accessed via `get_user_model()`.
- The APIClient from Django REST Framework is used to 
  simulate HTTP requests to the authentication endpoints.
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
def test_create_user_with_required_fields(api_client):
    """Test creating a user with all required fields using Djoser API."""
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'last_name' : 'Dillinger',
        'password': 'password123!@#',
    }

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username='testuser').exists()

    # Verifying the password is stored correctly
    user = User.objects.get(username='testuser')
    assert user.check_password('password123!@#')


@pytest.mark.django_db
def test_first_name_required(api_client):
    """Test that first_name is required for user creation using Djoser API."""
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'password': 'password123!@#',
        'email': 'testuser@example.com'
    }

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'first_name' in response.data


@pytest.mark.django_db
def test_last_name_optional(api_client):
    """Test that last_name is optional and defaults to an empty string using Djoser API."""
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'password': 'password123!@#',
        'email': 'testuser@example.com'
    }

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # Verifying the user has been created with an empty last_name
    user = User.objects.get(username='testuser')
    assert user.last_name in ['', None]
    assert user.email == 'testuser@example.com'

@pytest.mark.django_db
def test_last_name_is_text_field(api_client):
    """Test that last_name can handle a long string, which is typical for a TextField."""
    url = '/auth/users/'
    long_last_name = 'Dillinger' * 100  # A very long last name to test TextField behavior
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'last_name': long_last_name,
        'password': 'password123!@#',
        'email': 'testuser@example.com'
    }

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # Fetch the user from the database and verify last_name is stored correctly
    user = User.objects.get(username='testuser')
    assert user.last_name == long_last_name, "The last_name field should store long text."


@pytest.mark.django_db
def test_username_required(api_client):
    """Test that username is required for user creation using Djoser API."""
    url = '/auth/users/'
    data = {
        'first_name': 'John',
        'password': 'password123!@#',
    }

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data  # Check that the response contains a 'username' error


@pytest.mark.django_db
def test_username_unique(api_client):
    """Test that the username must be unique using Djoser API."""
    # First, create a user with the username 'testuser'
    User.objects.create_user(username='testuser', first_name='John', password='password123')

    # Attempt to create another user with the same username
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'Jane',
        'password': 'password123!@#',
        'email': 'testuser@example.com'
    }

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data  # Check that the response contains a 'username' error


@pytest.mark.django_db
def test_password_min_length(api_client):
    """Test that the password must meet the minimum length requirement using Djoser API."""
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'password': 'p123',  # Password too short
    }

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in response.data

@pytest.mark.django_db
def test_jwt_authentication(api_client):
    """Test JWT token creation with valid credentials."""
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'last_name' : 'Dillinger',
        'password': 'password123!@#',
        'email': 'testuser@example.com'
    }

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # Log in to get a JWT token
    response = api_client.post(
        '/auth/jwt/create/',
        {'username': 'testuser', 'password': 'password123!@#'}
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_invalid_jwt_authentication(api_client):
    """Test that invalid credentials do not authenticate the user."""
    response = api_client.post(
        '/auth/jwt/create/',
        {'username': 'testuser', 'password': 'wrongpassword'}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED  # Unauthorized
    assert 'access' not in response.data


@pytest.mark.django_db
def test_refresh_jwt_token(api_client):
    """Test refreshing the JWT token with a valid refresh token."""
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'last_name' : 'Dillinger',
        'password': 'password123!@#',
        'email': 'testuser@example.com'
    }

    registration_response = api_client.post(url, data, format='json')
    assert registration_response.status_code == status.HTTP_201_CREATED

    # Get the JWT tokens
    response = api_client.post(
        '/auth/jwt/create/',
        {'username': 'testuser', 'password': 'password123!@#'}
    )
    refresh_token = response.data['refresh']

    # Refresh the JWT token
    refresh_response = api_client.post('/auth/jwt/refresh/', {'refresh': refresh_token})
    assert refresh_response.status_code == status.HTTP_200_OK
    assert 'access' in refresh_response.data


@pytest.mark.django_db
def test_access_protected_view_with_jwt(api_client):
    """Test accessing a protected view using a valid JWT token."""
    # Create a user and get tokens
    url = '/auth/users/'
    data = {
        'username': 'testuser',
        'first_name': 'John',
        'last_name' : 'Dillinger',
        'password': 'password123!@#',
        'email': 'testuser@example.com'
    }

    registration_response = api_client.post(url, data, format='json')
    assert registration_response.status_code == status.HTTP_201_CREATED

    login_data = {'username': 'testuser', 'password': 'password123!@#'}
    login_response = api_client.post('/auth/jwt/create/', login_data, format='json')

    access_token = login_response.data['access']
    assert access_token is not None, "No access token returned"

    # Set the Authorization header with the token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Access a protected view (e.g., user details)
    response = api_client.get('/auth/users/me/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == 'testuser'

@pytest.mark.django_db
def test_access_protected_view_with_invalid_jwt(api_client):
    """Test accessing a protected view using an invalid JWT token."""
    # Use an invalid JWT token
    invalid_access_token = 'invalidtoken12345'  # Using an obviously invalid token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {invalid_access_token}')

    # Try to access a protected view (e.g., user details)
    response = api_client.get('/auth/users/me/')

    # Assert that the response status is HTTP 401 Unauthorized
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
