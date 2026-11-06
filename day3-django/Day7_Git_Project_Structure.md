# Day 7: Git and Project Structure

## Objective

Improve the Django recruitment backend structure, environment configuration,
dependency tracking, Git hygiene, and separation of concerns without changing
the existing Day 3-6 models, relationships, APIs, or migration history.

## Existing Project Structure

Before the refactor, the project contained:

```text
day3-django/
├── config/
├── core/
├── recruitment/
├── manage.py
└── db.sqlite3
```

`core` contained the Day 4 API models and views. `recruitment` contained the
recruitment domain models and admin registrations. The project had no
requirements file or environment template, and the settings module contained a
hard-coded development secret.

## Updated Project Structure

```text
day3-django/
├── apps/
│   ├── __init__.py
│   ├── core/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── recruitment/
│       ├── migrations/
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       └── tests.py
├── config/
├── services/
│   └── __init__.py
├── utils/
│   └── __init__.py
├── .env
├── .env.example
├── .gitignore
├── manage.py
└── requirements.txt
```

The local `db.sqlite3` and `.venv/` remain available for development but are
ignored by Git. The `screenshots/` directory can be added locally for
submission screenshots without affecting application code.

## Git and GitHub Workflow

The existing remote repository is reused. The intended workflow is:

```text
git status
git switch -c feature/day7-clean-architecture
git diff --cached
git commit -m "refactor: organize Django project and configure environment"
git push -u origin feature/day7-clean-architecture
```

The commit and push are performed only after reviewing the staged file list
and obtaining approval.

## `.gitignore` Explanation

`.gitignore` excludes virtual environments, Python bytecode and caches,
environment secrets, the local SQLite database, user media, collected static
files, IDE metadata, and common operating-system temporary files. This keeps
machine-specific files and secrets out of commits.

## `.env` and `.env.example`

`.env` stores local values for `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS`. It is
ignored by Git and must never be committed. `.env.example` contains only
placeholder values so another developer can create a local `.env` safely.
`config/settings.py` loads `.env` with `python-dotenv` and fails explicitly if
`SECRET_KEY` is missing.

## `requirements.txt`

The file pins the dependencies used by this project:

- Django
- Django REST Framework
- python-dotenv

The project virtual environment was installed from this file.

## Refactoring and Separation of Concerns

- Django apps are grouped under `apps/`.
- `AppConfig.name` and `INSTALLED_APPS` use the new package paths.
- API routing points to `apps.core.urls`.
- Existing model labels, migration files, relationships, and database tables
  remain unchanged.
- Views continue to handle HTTP requests and responses.
- Serializers continue to handle API representation and validation.
- `services/` and `utils/` are ready as Python packages for future business
  logic and reusable helpers without adding speculative code.
- Unused boilerplate test imports and duplicate URL imports were removed.

## Commands Used

```text
python -m pip install -r requirements.txt
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python manage.py showmigrations
python manage.py test
```

## Testing Results

- `manage.py check`: passed; no issues identified.
- `makemigrations --check --dry-run`: passed; no changes detected.
- `migrate --check`: passed.
- `showmigrations`: passed; existing `core` and `recruitment` migrations are
  applied along with Django migrations.
- `manage.py test`: passed; 0 tests were discovered because the existing test
  modules contained no test cases.
- API verification: `/api/`, `/api/jobs/`, and `/api/users/test/` returned
  HTTP 200.
- Admin verification: `/admin/` returned HTTP 302 for unauthenticated access.
- All four recruitment models are registered in the admin site.
- Existing model table names and application relationships were verified.
- `.env`, `db.sqlite3`, and `.venv/` are ignored by Git.

## Screenshots to Capture

Capture these for the internship submission:

1. The updated project tree in VS Code Explorer.
2. `config/settings.py` showing dotenv loading without revealing `.env`.
3. `.env.example` and `.gitignore`.
4. Successful `python manage.py check` output.
5. Successful migration commands and `showmigrations`.
6. API responses for the existing endpoints.
7. Django admin model list.
8. `git status`, staged diff summary, branch, and final push result.

Do not include the contents of `.env`, credentials, or the local database in
screenshots.

## Conclusion and Learning Outcomes

The backend now has a scalable app layout, explicit environment management,
reproducible dependencies, safer Git defaults, and documented validation
steps. The refactor demonstrates how to improve maintainability while
preserving an existing Django API and migration history.
