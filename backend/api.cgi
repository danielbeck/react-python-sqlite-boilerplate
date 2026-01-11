#!/usr/bin/env python3

import os
from wsgiref.handlers import CGIHandler

# The deploy script will replace the placeholder `__DEPLOY_BACKEND_DIR__`
# with the host-specific absolute backend path (backendRoot + baseDir + subDir + 'backend').
_backend_dir = "__DEPLOY_BACKEND_DIR__"
os.environ.setdefault('APP_BASE_DIR', _backend_dir)

import sys
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app import app

# Ensure backend logs directory exists (helps when deploy replaced the placeholder)
try:
    logs_dir = os.path.join(_backend_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
except Exception:
    pass

# Import a small helper that writes tracebacks into backend/logs (if available)
try:
    import logging_helper
except Exception:
    logging_helper = None

try:
    CGIHandler().run(app.wsgi_app)
except Exception:
    try:
        if logging_helper:
            logging_helper.log_exception()
    except Exception:
        pass
    raise
