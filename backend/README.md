# Backend README

## Overview

This backend provides a REST API for managing items, using Python Flask and SQLite. It is designed to run both as a Flask server (for local development) and as a CGI application (for shared hosting environments).

## Directory Structure and File Explanations

- **app.py**: Main Flask application. Sets up the app, logging, error handling, database helpers, and registers all endpoints (via Blueprints).
- **api.cgi**: CGI entry point for running the Flask app under CGI. Handles environment setup and error logging for CGI deployments.
- **config_helper.py**: Utility for reading deployment configuration from config.json and determining backend paths.
- **init_db.py**: Script to initialize the SQLite database and create sample data.
- **logging_helper.py**: Helper for logging exceptions from CGI scripts to backend/logs/cgi_error.log.
- **requirements.txt**: Python dependencies for the backend (Flask, Flask-CORS, etc).
- **endpoints/**: Directory containing modularized Flask Blueprints for each API endpoint.
    - **items.py**: Blueprint for all /items endpoints (CRUD for items).
- **database/**: Contains the SQLite database file (app.db).
- **logs/**: Stores log files for Flask and CGI error logging.
    - **flask_error.log**: Logs unhandled exceptions from Flask app.
    - **cgi_error.log**: Logs exceptions from CGI scripts.
    - **server.log**: (Optional) General server logs.
- **__pycache__/**: Python bytecode cache (auto-generated).

## Setup

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
