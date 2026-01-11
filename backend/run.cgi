#!/usr/bin/env python3
"""Alias CGI to test provider filename sensitivity.

This is intentionally identical to `api.cgi`'s minimal wrapper.
"""
import os
import sys
from wsgiref.handlers import CGIHandler

_backend_dir = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('APP_BASE_DIR', _backend_dir)
try:
    os.chdir(_backend_dir)
except Exception:
    pass
try:
    from app import app
except Exception:
    import traceback
    traceback.print_exc(file=sys.stderr)
    try:
        sys.stdout.write('Status: 500 Internal Server Error\r\n')
        sys.stdout.write('Content-Type: text/plain\r\n\r\n')
        sys.stdout.write('Internal server error\n')
        sys.stdout.flush()
    except Exception:
        pass
    sys.exit(1)
CGIHandler().run(app.wsgi_app)
