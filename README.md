# react-python-sqlite-boilerplate

A small React frontend paired with a Python/Flask backend (SQLite) — configured to run locally for development and as a CGI-backed app on shared hosting.

THe backend currently contains a demo "Todo List" app, as is traditional.

Modify config.json to deploy to different subdirectories or domains

## Quick links
- Backend: backend/app.py
- DB schema + sample data: backend/init_db.py
- Deploy script: deploy.sh
- Config: config.json

## Run locally

Backend (development)

```bash
cd backend
# optional: python3 -m venv .venv && source .venv/bin/activate
pip3 install -r requirements.txt
python3 init_db.py    # creates database/app.db and sample items
DEBUG=1 python3 app.py
```

Service listens on http://127.0.0.1:8000 by default.

Frontend (development)

```bash
cd frontend
npm install
npm run dev
```

Dev frontend runs on http://localhost:3000 and proxies API requests to the backend.  `npm run dev` will also start the backend server.

## API (current)

- GET / — root info
- GET /items — list items (returns `{ items: [...] }`)
- POST /items — create item (JSON body with `name`, optional `description`)
- GET /items/<id> — fetch item
- PUT /items/<id> — update item
- DELETE /items/<id> — delete item


See `backend/app.py` for authoritative endpoint behavior.

## Database

SQLite DB: `backend/database/app.db`.
To initialize or reset sample data:

```bash
python3 backend/init_db.py
```

## Deployment

The deployment process is managed by the `deploy.sh` script, which uses `config.json` for all environment and path settings.

### Standard Deploy

```bash
./deploy.sh
```
- Syncs backend and frontend code to the configured remote directory.
- Installs backend Python dependencies in a virtual environment (if not already present).
- Initializes the backend database **only if** this is the first deploy (i.e., the backend directory did not previously exist).
- Does **not** overwrite an existing database or sample data on redeploys.

### Force Fresh Deploy (reset database/sample data)

```bash
./deploy.sh --force-fresh
```
- Performs all steps of a standard deploy.
- **Always** (re)initializes the backend database by running `init_db.py` on the server, even if the backend directory already exists.
- This will recreate tables if missing and insert sample data if the items table is empty. Existing data is preserved unless the schema is missing.

**Note:**
- The deploy script uses SSH and rsync. You must have SSH access to the configured host.
- The backend virtual environment and dependencies are managed automatically on the server.
- The frontend is built locally and deployed to the correct subdirectory as configured.

See `deploy.sh` for full details and customization options.

