# Student Management System

A Django application for managing student records and user accounts.

## Setup

Use Python 3.12 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the application or
`http://127.0.0.1:8000/admin/` for Django Admin.

Superusers can open the user-management page at
`http://127.0.0.1:8000/user-management/`.

## Configuration

For deployment, set `DJANGO_SECRET_KEY` to a private, randomly generated key,
set `DJANGO_DEBUG=False`, and configure `ALLOWED_HOSTS` in
`StudentManagementSystem/settings.py`. Never commit passwords, environment
files, or the local SQLite database.
