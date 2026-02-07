from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import logging
import traceback
from collections import deque

app = Flask(__name__)
# Allow credentials and allow frontend dev origins (ports 3000-3010 for flexibility)
CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:3005"
])

# Setup file logging for unexpected exceptions (helps when running under CGI/Apache)
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'flask_error.log')
try:
    logs_dir = os.path.dirname(log_path)
    os.makedirs(logs_dir, exist_ok=True)
except Exception:
    pass
handler = logging.FileHandler(log_path)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


def _trim_log(path, max_lines=10000):
    try:
        # read last max_lines and rewrite file to keep size bounded
        with open(path, 'r') as f:
            dq = deque(f, maxlen=max_lines)
        with open(path, 'w') as f:
            f.writelines(dq)
    except Exception:
        pass

# Database path
# Prefer APP_BASE_DIR set by `api.cgi` when running under CGI/chroot.
BASE_DIR = os.environ.get('APP_BASE_DIR') or os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'app.db')

# Debug: log APP_BASE_DIR and DB_PATH to flask_error.log
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'flask_error.log'), 'a') as f:
        f.write(f"[DEBUG] APP_BASE_DIR: {BASE_DIR}\n")
        f.write(f"[DEBUG] DB_PATH: {DB_PATH}\n")
except Exception:
    pass

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row))

# ============ ROOT ENDPOINT ============

@app.route('/')
def index():
    return jsonify({
        'message': 'Boilerplate API',
        'endpoints': ['/items']
    })



# Register Blueprints for endpoints


try:
    # If run as module (python3 -m backend.app)
    from backend.endpoints.items import bp as items_bp
    from backend.endpoints.auth import bp as auth_bp
except ImportError:
    # If run as script (python3 app.py)
    from endpoints.items import bp as items_bp
    from endpoints.auth import bp as auth_bp

# Provide DB helpers to Blueprints via app config

app.config['get_db'] = get_db
app.config['dict_from_row'] = dict_from_row

# Security: Require SECRET_KEY in production
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('FLASK_ENV') == 'production':
        raise ValueError(
            "SECRET_KEY environment variable must be set in production. "
            "Generate one with: python3 -c 'import secrets; print(secrets.token_hex(32))'"
        )
    else:
        # Only use fallback in development
        import warnings
        warnings.warn(
            "Using insecure default SECRET_KEY. Set SECRET_KEY environment variable for production.",
            UserWarning
        )
        SECRET_KEY = 'dev_secret_DO_NOT_USE_IN_PRODUCTION'

app.secret_key = SECRET_KEY
app.register_blueprint(items_bp)
app.register_blueprint(auth_bp)


@app.errorhandler(Exception)
def handle_exception(e):
    # Log full traceback to flask_error.log for postmortem
    try:
        tb = traceback.format_exc()
        app.logger.error('Unhandled exception: %s\n%s', e, tb)
    except Exception:
        pass
    try:
        _trim_log(log_path, max_lines=10000)
    except Exception:
        pass
    return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('DEBUG', '0') == '1'
    app.run(host='127.0.0.1', port=8000, debug=debug_mode)
