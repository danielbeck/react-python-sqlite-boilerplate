#!/usr/bin/env python3
# Minimal CGI wrapper using the known-good absolute backend path.
# This version was working on the host; reverting to it per request.
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

CGIHandler().run(app.wsgi_app)
