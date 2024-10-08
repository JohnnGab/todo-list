# ToDo list Application API

The ToDo List API Application allows users to manage tasks through a simple RESTful API. Users can register, authenticate via JWT tokens, and perform CRUD operations on tasks. Key features include task creation, updating, deletion, and filtering based on task status. Pagination is supported for task listings, and rate limiting is enforced with 1000 daily requests for authenticated users and 100 for anonymous users. Admin users can access all tasks, while regular users can manage only their own.

## Setup and Deployment

## Local Development

1. **Clone the Project Repository**:
    - Clone the project repository from the following link:
        - [Project Repository](https://github.com/JohnnGab/todo-list.git)
    - You can use Git to clone the repository with the following command:
        ```bash
        git clone https://github.com/JohnnGab/todo-list.git
        ```

2. **Navigate to the Project Directory**:
    - Change your working directory to the root directory of the cloned project:
        ```bash
        cd todo-list
        ```

3. **Build the Docker Containers**:
    - Make sure you have Docker installed on your system and is running.
    - Run the following command to build the Docker image:
        ```bash
        docker-compose build
        ```

4. **Start the Containers**:
    - Once the image is built, you can run the Docker container with the following command:
        ```bash
        docker-compose up
        ```
    - This command will start the container and map port `8000` from the container to port `8000` on your host machine.
5. **Access the Django App**
    - Once the containers are running, the Django app will be available on http://127.0.0.1:8000.


# API Documentation

## User Registration
**Endpoint:** POST /auth/users/

**Description:**  
This endpoint allows users to register by providing their username, password, and other required fields.

**Required Fields:** 
- `username` (string)
- `password` (string)
- `first_name` (string)

**Optional Fields:**
- `last_name` (string)
- `email` (string)

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/users/" \
 -H "Content-Type: application/json" \
 -d '{"username": "john_doe", "password": "securepassword", "first_name": "John"}'
```
**Note:** The password must be at least 6 characters long and should not be too common.


## Obtain JWT Token
**Endpoint:** POST /auth/jwt/create/

**Description:**
This endpoint allows users to obtain a JSON Web Token (JWT) for authenticating subsequent requests.

**Required Fields:**
- `username` (string)
- `password` (string)

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/jwt/create/" \
 -H "Content-Type: application/json" \
 -d '{"username": "john_doe", "password": "securepassword"}'
```


## Refresh JWT Token
`Endpoint:` POST /auth/jwt/refresh/

**Description:** 
This endpoint allows users to refresh their access token using a valid refresh token obtained from the /auth/jwt/create/ endpoint. It is used to get a new access token when the current one is expired. After refreshing, the used refresh token is blacklisted and cannot be used again, ensuring enhanced security.

**Required Fields:**
`refresh:` (string) The refresh token obtained during login.


## List Tasks 
**Endpoint:** GET api/tasks/?page_size={page_size}

**Description:**
This endpoint allows admin users to retrieve all tasks in the system. Regular users will only see their own tasks.

**Authentication Required:** Yes (JWT Token)

**Supports Pagination**: Yes (Pagination parameters can be included in query params). 
- `default_page_size` : 10, 
- `max_page_size` : 100

**Example Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/tasks/?page_size=20" \
  -H "Authorization: Bearer your-jwt-access-token"
```


## Retrieve a Task
**Endpoint:** GET api/tasks/{id}/

**Description:**
Retrieve the details of a specific task by its ID.

**Authentication Required:** Yes (JWT Token)

**Example Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/tasks/1/" \
  -H "Authorization: Bearer your-jwt-access-token"
```


## Create a Task
**Endpoint:** POST api/tasks/

**Description:**
This endpoint allows users to create a new task.

**Required Fields:**
- `title:` (string) 
- `description:` (string) 
- `status:` (string) (case-sensitive) The current status of the task. Choices(case-sensitive): New, In Progress, Completed.

**Authentication Required:** Yes (JWT Token)

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/tasks/" \
  -H "Authorization: Bearer your-jwt-access-token" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "description": "This is a new task.", "status": "New"}'
```


## Update a Task
**Endpoint:** PUT api/tasks/{id}/

**Description:**
This endpoint allows users to update an existing task.

**Required Fields:**
- `title:` (string)
- `description:` (string)
- `status:` (string) The current status of the task. Choices(case-sensitive): New, In Progress, Completed.

**Authentication Required:** Yes (JWT Token)

**Example Request:**
```bash
curl -X PUT "http://127.0.0.1:8000/api/tasks/1/" \
  -H "Authorization: Bearer your-jwt-access-token" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task", "description": "This is an updated task.", "status": "In Progress"}'
```


## Partially Update a Task
**Endpoint:** PATCH api/tasks/{id}/

**Description:**
This endpoint allows users to partially update an existing task. Can be used to mark a task as completed.
status filed is case-sensitive.
**Authentication Required:** Yes (JWT Token)

**Example Request:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/tasks/1/" \
  -H "Authorization: Bearer your-jwt-access-token" \
  -H "Content-Type: application/json" \
  -d '{"status": "Completed"}'
```

## Delete a Task
**Endpoint:** DELETE /tasks/{id}/

**Description:**
This endpoint allows users to delete a task by its ID.

**Authentication Required:** Yes (JWT Token)

**Example Request:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/tasks/1/" \
  -H "Authorization: Bearer your-jwt-access-token"
```

## Filtering Tasks
**Endpoint:** GET /tasks/?status={status}

**Description:**
Filter tasks based on their status. The allowed status values (case-sensitive) are New, In Progress, and Completed.

**Authentication Required:** Yes (JWT Token)

**Example Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/tasks/?status=Completed" \
  -H "Authorization: Bearer your-jwt-access-token"
```


## Rate Limiting:

- `Anonymous users:` 100 requests per day (anon: 100/day)
- `Authenticated users:` 1000 requests per day (user: 1000/day)
Exceeding these limits will result in an HTTP 429 (Too Many Requests) response.


## JWT
Acsess token duration is set to 1 hour. Refresh token's to 1 day.

**ALLOWED HOSTS**:
- 'localhost', '127.0.0.1'

## Testing:

 1. To manually test, you can use tools like Postman, curl, or similar alternatives.
    `Note:` Database will be empty
    - `URL:` http://127.0.0.1:8000.
    - `Superuser:` username : admin; password: Admin123@
  2. Run Unit Tests (pytest):
     ```bash
     # In terminal or cmd change your working directory to the root directory of the cloned project enter the Running web Container'
     docker-compose exec web bash
     #'Run pytest
     pipenv run pytest -v
     # Exit the container 
     exit
     ```


## Unit Tests:
- `Create task with valid JWT token:` Verify that a user can create a task when authenticated with a valid JWT token.
- `List tasks for each user:` Ensure that each user can retrieve their own tasks; one user has a task, and the other has none.
- `Admin can list all tasks:` Confirm that an admin user can retrieve all tasks in the system.
- `Retrieving a specific task:` Verify that a user can retrieve details of a specific task they own.
- `Owner can fully update task:` Ensure that the owner of a task can update all details of their task.
- `User cannot update unowned task:` Confirm that a user cannot update a task that they do not own.
- `Only task owner can delete task:` Verify that a task can only be deleted by its owner and not by other users.
- `Task owner can mark task as completed:` Ensure that the owner can update the task's status to 'Completed'.
- `Filter tasks by status:` Verify that tasks can be filtered by status, retrieving tasks matching a specific status.
- `Create user with required fields:` Verify that a user can be created when all required fields are provided via Djoser API.
- `first_name is required for user creation:` Ensure that user creation fails if first_name is not provided.
- `last_name is optional:` Confirm that last_name is optional and defaults to an empty string if not provided.
- `last_name accepts long strings:` Verify that the last_name field can handle long text, as appropriate for a TextField.
- `Username is required for user creation:` Ensure that user creation fails if username is not provided.
- `Username must be unique:` Confirm that a user cannot be created with a username that already exists.
- `Password minimum length requirement:` Verify that user creation fails if the password does not meet the minimum length (6) requirement.
- `JWT token creation with valid credentials:` Ensure that a JWT token can be obtained with valid user credentials.
- `JWT authentication with invalid credentials:` Confirm that authentication fails and no token is returned when credentials are invalid.
- `Refreshing JWT token:` Verify that an access token can be refreshed using a valid refresh token.
- `Access protected view with valid JWT:` Ensure that protected endpoints can be accessed when a valid JWT access token is provided.
- `Access protected view with invalid JWT`: Confirm that access is denied when an invalid JWT access token is used to access protected endpoints.


## Note:
The Django REST Framework (DRF) browsable API won't function properly in this project for two reasons:

  1. Static Files Not Loading: With DEBUG = False, Django doesn't serve static files (CSS, JS), breaking the 
     browsable API's interface.

  2. Incompatibility with JWT Authentication: The browsable API relies on session-based authentication, but 
     this project uses JWT, which it doesn't support by default. As a result, you can't authenticate or interact with protected endpoints.