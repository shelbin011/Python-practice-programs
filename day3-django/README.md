# Zecpath ATS – Backend

## Project Overview

Zecpath ATS is an Applicant Tracking System (ATS) and Job Portal backend developed using Django and Django REST Framework.

The platform supports candidate and employer operations, job management, applications, profile management, resume uploads, and JWT-based authentication.

## Technology Stack

- Python
- Django
- Django REST Framework
- SQLite
- SimpleJWT
- django-filter
- Postman

## Main Features

### Authentication
- User registration
- Email-based login
- JWT access and refresh tokens
- Token refresh and rotation
- Logout with refresh-token blacklisting

### User Roles
- Admin
- Employer
- Candidate

### Job Management
- Public job listing
- Employer job creation and management
- Job filtering and keyword search
- Pagination

### Candidate Features
- Candidate profile management
- Job applications
- Application tracking
- Resume upload, retrieval, replacement, and deletion

### Employer Features
- Employer profile management
- Job management
- Candidate application listing

### Admin Features
- User listing
- Account activation and deactivation

## Installation and Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env`.
5. Apply migrations:

```bash
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

## Security Features

- JWT authentication
- Role-based access control
- Password validation
- Refresh-token rotation and blacklisting
- Resume file size and extension validation
- User-specific resource access restrictions

## API Documentation

API endpoints are organized into authentication, recruitment, employer, candidate, and admin modules.

Postman is used for API testing.

## Development Status

Backend implementation and API testing are ongoing as part of the Zecpath internship.