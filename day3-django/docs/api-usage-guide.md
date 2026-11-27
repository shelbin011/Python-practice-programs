
# Zecpath ATS – API Usage Guide

## 1. Base URL

Local development:

http://127.0.0.1:8000

## 2. Authentication APIs

### 2.1 User Signup

**Endpoint:** `/api/auth/signup/`

**Method:** POST

**Request Body:**

```json
{
    "name": "Test Candidate",
    "email": "candidate@example.com",
    "password": "StrongPassword@123"
}
```

**Expected Response:** 201 Created

Registers a new candidate account.

### 2.2 User Login

**Endpoint:** `/api/auth/login/`

**Method:** POST

**Request Body:**

```json
{
    "email": "candidate@example.com",
    "password": "StrongPassword@123"
}
```

**Expected Response:** 200 OK

Returns:
- Access token
- Refresh token
- User information

### 2.3 Refresh Token

**Endpoint:** `/api/auth/refresh/`

**Method:** POST

**Request Body:**

```json
{
    "refresh": "<refresh_token>"
}
```

**Expected Response:** 200 OK

Generates a new access token and, with rotation enabled, a new refresh token.

### 2.4 User Logout

**Endpoint:** `/api/auth/logout/`

**Method:** POST

**Authorization:** Bearer access token

**Request Body:**

```json
{
    "refresh": "<refresh_token>"
}
```

**Expected Response:** Successful logout response.

The refresh token is blacklisted to prevent reuse.

## 3. JWT Authentication

Protected APIs require an access token.

**Authorization Header:**

```text
Authorization: Bearer <access_token>
```

## 4. HTTP Status Codes

| Status Code | Meaning |
|---|---|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

## 5. Role-Based Access

The application supports three main roles:

- Admin
- Employer
- Candidate

Each role has access to specific APIs based on its permissions.

## 6. Pagination

List APIs support page-number pagination.

Example:

`GET /api/recruitment/jobs/?page=1`

Default page size: 10 records.

## 7. Filtering

Public job listing supports filtering by location and employer.

Examples:

`GET /api/recruitment/jobs/?location=Kochi`

`GET /api/recruitment/jobs/?employer=2`

## 8. Searching

Public job listing supports keyword search across title, description and location.

Example:

`GET /api/recruitment/jobs/?search=Python`

## 9. Combined Search and Filtering

Example:

`GET /api/recruitment/jobs/?search=Python&location=Kochi`

## 10. Important Security Notes

- Never expose access or refresh tokens.
- Do not store passwords in plain text.
- Use HTTPS in production.
- Keep environment secrets outside source control.
- Use the correct role and permissions for protected endpoints.
