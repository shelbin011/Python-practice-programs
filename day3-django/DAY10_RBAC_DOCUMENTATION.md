# Day 10: Role-Based Access Control

## What is RBAC?

Role-Based Access Control (RBAC) grants permissions through roles instead of
individual user IDs. Zecpath uses Django Groups for the `Admin`, `Employer`,
and `Candidate` roles, with Django's `is_staff` and `is_superuser` flags also
recognized as administrative privileges.

The role is read from the authenticated Django user. It is never accepted
from request payloads or trusted to frontend controls.

## Why RBAC matters in SaaS applications

Recruitment data is shared across multiple organizations and user types.
RBAC provides a consistent server-side boundary so that:

- Employers manage only their own jobs and applications.
- Candidates manage only their own applications.
- Administrators can monitor and manage platform-wide data.
- Public users can see only explicitly public job information.

## Permission classes

The custom classes are in `apps/recruitment/permissions.py`:

- `IsAdmin`: allows staff, superusers, or users in the `Admin` group.
- `IsEmployer`: allows authenticated users in the `Employer` group.
- `IsCandidate`: allows authenticated users in the `Candidate` group.
- `IsAdminOrReadOnly`: permits safe HTTP methods and restricts writes to
  administrators.
- `IsEmployerOwner`: combines Employer access with job ownership checks.
- `IsCandidateOwner`: combines Candidate access with application ownership
  checks.

Unauthenticated requests are rejected by DRF/JWT authentication. Authenticated
users with an incorrect role receive `403 Forbidden`.

## Middleware

No custom role middleware was added. Django's authentication middleware and
DRF's configured SimpleJWT authentication already identify the request user.
Authorization stays in DRF permission classes and queryset filtering, which
avoids duplicating JWT logic and does not interfere with public endpoints.

## Role-to-API access matrix

| API | Public | Candidate | Employer | Admin |
|---|---:|---:|---:|---:|
| `GET /api/recruitment/jobs/` | Yes | Yes | Yes | Yes |
| Employer job list/create | No | No | Own jobs | No |
| Employer job update/delete | No | No | Own jobs only | No |
| Employer application list | No | No | Own jobs only | No |
| Candidate application list/create | No | Own applications | No | No |
| Candidate application update/delete | No | Own applications only | No | No |
| Admin user list | No | No | No | Yes |
| Admin account status update | No | No | No | Yes |

The existing legacy `POST /api/jobs/create/` endpoint is also restricted to
the Employer group. The existing authenticated sample job list remains
available to authenticated users for backwards compatibility.

## Object-level ownership

Employer querysets are filtered by `job__employer__user=request.user`, so
another employer's job is not returned or modified. Candidate application
querysets are filtered by `candidate__user=request.user`, so another
candidate's application is not exposed.

The application API derives the candidate from the authenticated user and the
job employer is assigned from the authenticated employer profile. Clients
cannot submit a different owner. Cross-owner detail requests return `404` to
avoid confirming the existence of private objects.

## Endpoint documentation

### Public jobs

`GET /api/recruitment/jobs/`

Returns active job listings without requiring authentication.

### Employer jobs

`GET /api/recruitment/employer/jobs/`

Returns only the authenticated employer's jobs.

`POST /api/recruitment/employer/jobs/`

```json
{
  "title": "Django Developer",
  "description": "Build Django services",
  "location": "Remote"
}
```

`PATCH` and `DELETE /api/recruitment/employer/jobs/<id>/` operate only on the
authenticated employer's own job.

### Employer applications

`GET /api/recruitment/employer/applications/`

Returns applications for jobs owned by the authenticated employer.

### Candidate applications

`GET /api/recruitment/candidate/applications/` returns the candidate's own
applications.

`POST /api/recruitment/candidate/applications/`

```json
{
  "job_id": 1
}
```

`PATCH`, `DELETE`, and `GET /api/recruitment/candidate/applications/<id>/`
are restricted to the owning candidate.

### Admin APIs

`GET /api/recruitment/admin/users/` lists users with non-sensitive account and
group information.

`PATCH /api/recruitment/admin/users/<id>/status/` accepts only:

```json
{
  "is_active": false
}
```

Role, group, staff, superuser, username, and email fields are rejected rather
than changed through this endpoint. Administrators cannot deactivate their own
account.

## Testing scenarios and results

The RBAC test suite in `apps/recruitment/tests.py` covers:

1. Admin access to the admin API.
2. Employer job creation and own-job access.
3. Candidate application creation and own-application access.
4. Candidate job-creation rejection.
5. Employer application rejection.
6. Candidate and Employer admin-access rejection.
7. Cross-employer job modification rejection.
8. Cross-candidate application access rejection.
9. Unauthenticated protected-endpoint rejection.
10. Role-field modification rejection.
11. Public job-list access.

Existing JWT tests remain enabled and pass alongside the RBAC tests.

## Security improvements

- Server-side group and admin privilege checks.
- Ownership filtering at the queryset level.
- Object-level ownership permission classes.
- Public listings limited to active jobs.
- Candidate and employer role separation.
- Owner fields are assigned from the authenticated user.
- Sensitive role and identity fields cannot be changed through the status API.
- Existing JWT authentication and password protections remain unchanged.

## Run and verify

```powershell
cd D:\python-intern\day3-django
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py test
python manage.py runserver
```
