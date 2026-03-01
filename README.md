# Task Manager API

A Django REST API for task management with JWT authentication, role-based access, session-backed logout, filtering, and pagination.

## Overview

- Task CRUD for authenticated users
- Custom `User` model with roles (`admin`, `user`)
- JWT auth with DB-backed sessions (`UserSession`)
- Logout support by expiring current session
- Search, filter, ordering, pagination on task list
- Interactive docs via Swagger and ReDoc
- Unit test coverage for auth and task flows

## Tech Stack

- Python, Django, Django REST Framework
- SimpleJWT
- SQLite (default)
- django-filter
- drf-spectacular (OpenAPI/Swagger/ReDoc)

## Project Structure

```text
task/
├── manage.py
├── README.md
├── API_EXAMPLES.md
├── taskmanager/
│   ├── settings.py
│   └── urls.py
├── users/
│   ├── models.py
│   ├── authentication.py
│   ├── views/
│   ├── service/
│   ├── repo/
│   ├── urls/
│   └── tests.py
└── tasks/
    ├── models.py
    ├── views/
    ├── service/
    ├── repo/
    ├── urls/
    └── tests.py
```

## Setup

1. Create and activate virtualenv:

```bash
python3 -m venv tenv
source tenv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Start server:

```bash
python manage.py runserver
```

Base URL: `http://127.0.0.1:8000`

## API Documentation

This project ships OpenAPI documentation using **drf-spectacular**.

- Swagger UI: `http://127.0.0.1:8000/api/docs`
- ReDoc: `http://127.0.0.1:8000/api/redoc`
- OpenAPI Schema: `http://127.0.0.1:8000/api/schema`

## Authentication

Login and registration return:

- `tokens.access` (use for protected endpoints)

Protected endpoints accept:

1. Standard header:
`Authorization: Bearer <ACCESS_TOKEN>`
2. Custom header (also supported in this project):
`access-token: <ACCESS_TOKEN>`

Note: use `access-token` (hyphen), not `access_token` (underscore).

## API Endpoints

All API routes are **slashless**.

### Auth Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/logout` | Logout current session |
| GET | `/api/auth/profile` | Get profile |
| PUT/PATCH | `/api/auth/profile` | Update profile |
| POST | `/api/auth/change-password` | Change password |

### Task Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks` | List tasks |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/{id}` | Retrieve task |
| PUT/PATCH | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| GET | `/api/tasks/stats` | Task statistics |

## Request/Response Examples

### Register

Request:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username":"john",
    "email":"john@example.com",
    "password":"TestPass123!",
    "password2":"TestPass123!",
    "first_name":"John",
    "last_name":"Doe"
  }'
```

Response (`201`):

```json
{
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "date_joined": "2026-03-01T10:00:00Z"
  },
  "tokens": {
    "access": "<access_token>"
  },
  "message": "User registered successfully"
}
```

### Login

Request:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"TestPass123!"}'
```

Response (`200`):

```json
{
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "date_joined": "2026-03-01T10:00:00Z"
  },
  "tokens": {
    "access": "<access_token>"
  },
  "message": "Login successful"
}
```

### Get Profile

Request:

```bash
curl -X GET http://127.0.0.1:8000/api/auth/profile \
  -H "Authorization: Bearer <access_token>"
```

Response (`200`):

```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "date_joined": "2026-03-01T10:00:00Z"
}
```

### Create Task

Request:

```bash
curl -X POST http://127.0.0.1:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "title":"Ship API docs",
    "description":"Finalize README and examples",
    "completed":false
  }'
```

Response (`201`):

```json
{
  "id": 1,
  "title": "Ship API docs",
  "description": "Finalize README and examples",
  "completed": false,
  "created_at": "2026-03-01T10:30:00Z",
  "updated_at": "2026-03-01T10:30:00Z",
  "owner": "john",
  "owner_id": 1
}
```

## Testing

Unit tests are available for both apps and cover common success/failure cases.

Run all tests:

```bash
python manage.py test
```

Run app-level tests:

```bash
python manage.py test users
python manage.py test tasks
```

