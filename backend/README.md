# Backend README

## Overview

This backend provides a REST API for managing items, using Python Flask and SQLite. It is designed to run both as a Flask server (for local development) and as a CGI application (for shared hosting environments).

## Directory Structure and File Explanations

- **app.py**: Main Flask application. Sets up the app, logging, error handling, database helpers, and registers all endpoints (via Blueprints).
- **api.cgi**: Shell CGI launcher that uses Apache's `SCRIPT_FILENAME` to run the adjacent virtualenv Python and `cgi_app.py`, avoiding unreliable Python shebangs and CGI working directories.
- **cgi_app.py**: Python CGI entry point; resolves its backend directory and logs startup/import failures in `logs/cgi_error.log`.
- **session_secret.py**: Loads the session signing key without a hardcoded fallback.
- **config_helper.py**: Utility for reading deployment configuration from config.json and determining backend paths.
- **init_db.py**: Script to initialize the SQLite database and create sample data.
- **logging_helper.py**: Helper for logging exceptions from CGI scripts to backend/logs/cgi_error.log.
- **requirements.txt**: Python dependencies for the backend (Flask, Flask-CORS, etc).
- **endpoints/**: Directory containing modularized Flask Blueprints for each API endpoint.
    - **items.py**: Blueprint for all /items endpoints (CRUD for items).
    - **auth.py**: Registration, login, logout, and current-user endpoints.
- **database/**: Contains the SQLite database file (app.db).
- **logs/**: Stores log files for Flask and CGI error logging.
    - **flask_error.log**: Logs unhandled exceptions from Flask app.
    - **cgi_error.log**: Logs exceptions from CGI scripts.
    - **server.log**: (Optional) General server logs.
- **__pycache__/**: Python bytecode cache (auto-generated).

## Setup

Set a random, stable `SECRET_KEY` in the project-root `.env`. Local startup
loads that key unless the process environment overrides it. Missing or empty
keys stop startup. Do not commit `.env` or copy it into the web root.

Deployment transfers only the key over SSH, without printing it, to
`~/.config/react-python-sqlite-boilerplate/session.json` outside the web root.
The directory uses permissions 700 and the file 600. CGI reads this private
file on every request; `APP_SECRET_FILE` overrides the path. Changing the key
invalidates existing sessions, not accounts or todos. For additional deployed
apps, use a distinct private path in both `deploy.sh` and `cgi_app.py`.

HTTP cookie settings are unchanged. `FLASK_ENV=production` enables secure-only
cookies and requires HTTPS. A secret key does not encrypt HTTP traffic.

Authentication uses Flask-Limiter's automatic request hook, not a manual
`check()` call on its extension, which newer releases store as a set.

Deployment checks that the virtualenv's recorded Python major/minor version
matches its interpreter and that pip is importable. Hosting Python upgrades can
invalidate an old virtualenv. In that case the old environment is preserved
under `backend/venv-backup.*/venv` and a fresh one is created. All dependencies
are installed using `venv/bin/python -m pip`; installation or import failures
stop deployment instead of falling back to an incomplete dependency list.

1. Install Python dependencies:
    ```bash
    pip3 install -r requirements.txt
    ```
2. Initialize the database:
    ```bash
    python3 init_db.py
    ```
    This will create:
    - `database/app.db` - SQLite database file
    - 3 sample items

3. Start the Flask development server:
    ```bash
    python3 app.py
    ```

## API Examples

- `POST /auth/register` and `POST /auth/login`: username/password JSON
- `POST /auth/logout`: clear the login session
- `GET /auth/me`: current username or `null`

The frontend uses the Vite `<BASE_URL>api` proxy in development and the CGI URL
in production. Backend JSON validation errors are shown on the account forms;
non-JSON responses explicitly report a backend/routing failure.

### Get All Items
```bash
curl http://localhost:8000/items
```

### Create New Item
```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"New Item","description":"Optional description"}'
```

### Update Item
```bash
curl -X PUT http://localhost:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Item","description":"New description"}'
```

### Delete Item
```bash
curl -X DELETE http://localhost:8000/items/1
```

## CORS

CORS is enabled using Flask-CORS to allow frontend access from any origin.
