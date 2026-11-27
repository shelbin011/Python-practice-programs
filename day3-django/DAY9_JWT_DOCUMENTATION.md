# Day 9: JWT Authentication

Zecpath uses JSON Web Tokens (JWTs) with Django REST Framework SimpleJWT.
Authentication uses Django's built-in `auth.User`, which is also the user
model referenced by the existing Employer and Candidate profile models.
The older `apps.core.User` model remains unchanged for the existing sample
API.

## JWT overview

JWT authentication lets a client prove its identity by sending a signed token
with each protected request. The server validates the token without storing
access tokens in the database.

- **Access token:** Short-lived token used in the `Authorization` header.
  It expires after 15 minutes.
- **Refresh token:** Longer-lived token used to obtain a new access token. It
  expires after one day and is rotated and blacklisted after use.

Passwords are stored using Django's password hashing. JWT signing uses the
project `SECRET_KEY`, which must be supplied through `.env`.

## Authentication workflow

1. Register with `POST /api/auth/signup/`.
2. Log in with `POST /api/auth/login/` to receive access and refresh tokens.
3. Send `Authorization: Bearer <access-token>` to protected endpoints.
4. When the access token expires, call `POST /api/auth/refresh/`.
5. On logout, send the refresh token to `POST /api/auth/logout/`.
6. The refresh token is blacklisted and cannot be reused.

New users receive the default `Candidate` group. Role-based permissions are
intentionally reserved for Day 10.

## API endpoints

### Signup

`POST /api/auth/signup/`

```json
{
  "name": "Asha Candidate",
  "email": "asha@example.com",
  "password": "StrongPassword123!"
}
```

Successful response (`201 Created`):

```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "email": "asha@example.com",
    "first_name": "Asha Candidate",
    "last_name": ""
  },
  "role": "candidate"
}
```

Email addresses are normalized and must be unique. Password validation uses
the configured Django password validators.

### Login

`POST /api/auth/login/`

```json
{
  "email": "asha@example.com",
  "password": "StrongPassword123!"
}
```

Successful response (`200 OK`):

```json
{
  "refresh": "<refresh-token>",
  "access": "<access-token>",
  "user": {
    "id": 1,
    "email": "asha@example.com",
    "first_name": "Asha Candidate",
    "last_name": ""
  }
}
```

Invalid credentials and inactive accounts return `401 Unauthorized`.

### Protected sample APIs

These existing sample APIs now require a valid access token:

- `GET /api/jobs/`
- `POST /api/jobs/create/`
- `GET /api/users/test/`

Requests without a token or with an invalid token return `401 Unauthorized`.
The health endpoint `GET /api/` remains public.

### Refresh

`POST /api/auth/refresh/`

```json
{
  "refresh": "<refresh-token>"
}
```

The response contains a new access token and, because rotation is enabled, a
new refresh token. The submitted refresh token is blacklisted.

### Logout

`POST /api/auth/logout/`

```json
{
  "refresh": "<refresh-token>"
}
```

Successful logout returns `200 OK`. The submitted refresh token
cannot be used again.

## Installation and configuration

From the `day3-django` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create `.env` from `.env.example` and set a strong local `SECRET_KEY`:

```text
SECRET_KEY=replace-with-a-local-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Apply migrations and start Django:

```powershell
python manage.py migrate
python manage.py check
python manage.py runserver
```

SimpleJWT is configured with a 15-minute access lifetime, one-day refresh
lifetime, refresh rotation, blacklisting, and JWT as the global DRF
authentication class.

## Postman testing

1. Send the signup request and confirm `201 Created`.
2. Repeat signup with the same email and confirm `400 Bad Request`.
3. Log in and save the returned access and refresh values.
4. Call `GET /api/jobs/` without authorization and confirm `401`.
5. Set Postman Authorization to **Bearer Token** with the access token and
   confirm the protected request succeeds.
6. Replace the access token with an invalid value and confirm `401`.
7. Refresh using the saved refresh token and save the rotated refresh token.
8. Try the original refresh token again and confirm it is rejected.
9. Log out using the rotated refresh token.
10. Try refreshing with the logged-out token and confirm it is rejected.

## Security features implemented

- Django password hashing through `create_user`.
- Django password validators and minimum password length.
- Case-insensitive email uniqueness validation.
- Inactive-account login protection.
- No client-controlled staff, superuser, or role fields.
- Public user responses exclude password and privilege fields.
- JWT authentication is the default DRF authentication mechanism.
- Refresh token rotation and blacklist-after-rotation.
- Explicit public permissions only for signup, login, refresh, and logout.
- Existing sample API endpoints require authentication.
