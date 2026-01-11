#!/bin/bash

# Deployment script - Deploys to configured directory
# Configuration is read from config.json

# Read configuration from config.json (use Python to parse and normalize)
if [ ! -f "config.json" ]; then
    echo "❌ config.json not found!"
    echo "Please create config.json with deployment settings"
    exit 1
fi

read -r HOST USER BASE_DIR SUB_DIR BACKEND_ROOT DOMAIN <<EOF
$(python3 - <<PY
import json
cfg = json.load(open('config.json'))
deployment = cfg.get('deployment', {})
production = cfg.get('production', {})
host = deployment.get('host', '')
user = deployment.get('user', '')
base = deployment.get('baseDir', '')
sub = deployment.get('subDir', '')
backend_root = deployment.get('backendRoot', '')
# Normalize: ensure base ends with a single '/'
if base and not base.endswith('/'):
    base = base + '/'
if base == '/':
    base = ''
# Normalize sub: remove any leading/trailing slashes, then append a trailing slash if non-empty
sub = sub.strip('/')
if sub:
    sub = sub + '/'
# Normalize backend_root to end with '/'
if backend_root and not backend_root.endswith('/'):
    backend_root = backend_root + '/'
print(host, user, base, sub, backend_root, production.get('domain', ''))
PY
)
EOF

# Construct full remote directory path
REMOTE_DIR="${BASE_DIR}${SUB_DIR}"

CONTROL_PATH="$HOME/.ssh/deploy-control-$$"

echo "🚀 Deploying to $USER@$HOST:$REMOTE_DIR"
echo "⚠️  This script will only modify the configured directory"
echo ""

# Establish persistent SSH connection
echo "📡 Establishing SSH connection..."
echo "   (You'll only need to enter your password once)"

ssh -o ControlMaster=auto \
    -o ControlPath="$CONTROL_PATH" \
    -o ControlPersist=10m \
    -fN $USER@$HOST

if [ $? -ne 0 ]; then
    echo "❌ Failed to establish SSH connection"
    exit 1
fi

sleep 1
echo "✅ Connection established"
echo ""

# Cleanup function to close SSH connection
cleanup() {
    echo ""
    echo "🔒 Closing SSH connection..."
    ssh -o ControlPath="$CONTROL_PATH" -O exit $USER@$HOST 2>/dev/null
    rm -f "$CONTROL_PATH"
}

trap cleanup EXIT

echo "📦 Deploying backend to ${REMOTE_DIR}backend/..."
echo "🗂️  Ensuring remote directories exist..."
# Check if backend directory exists before creating (to detect first-time deploy)
BACKEND_EXISTS=$(ssh -o ControlPath="$CONTROL_PATH" $USER@$HOST "if [ -d '${REMOTE_DIR}backend' ]; then echo 1; else echo 0; fi")
ssh -o ControlPath="$CONTROL_PATH" $USER@$HOST "mkdir -p ${REMOTE_DIR}backend ${REMOTE_DIR}frontend"
echo "✅ Remote directories ensured."
# Prepare a templated api.cgi with the computed backend dir and upload it
# Build and normalize backend dir by collapsing duplicate slashes
BACKEND_DIR="${BACKEND_ROOT}${BASE_DIR}${SUB_DIR}backend"
BACKEND_DIR=$(echo "${BACKEND_DIR}" | sed -E 's:/+:/:g')

# Rsync backend excluding api.cgi, then push a templated api.cgi with the correct backend path
rsync -avz --progress \
    -e "ssh -o ControlPath=$CONTROL_PATH" \
    --exclude='api.cgi' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='database/*.db' \
    --exclude='database/*.db-journal' \
    --exclude='venv/' \
    --exclude='.venv/' \
    --exclude='*.log' \
    --exclude='logs/' \
    --exclude='.git/' \
    --exclude='.DS_Store' \
    backend/ $USER@$HOST:${REMOTE_DIR}backend/

# Create a templated api.cgi locally with the correct backend path
TMP_API=$(mktemp /tmp/api.cgi.XXXX)
sed "s|__DEPLOY_BACKEND_DIR__|${BACKEND_DIR}|g" backend/api.cgi > "$TMP_API"
scp -o ControlPath="$CONTROL_PATH" "$TMP_API" $USER@$HOST:${REMOTE_DIR}backend/api.cgi
rm -f "$TMP_API"

# Harden permissions: remove group/world write bits on backend files and
# ensure CGI scripts are executable. Keep logs directory writable so the
# app can write logs (we create defaults only if missing).
echo "🔐 Hardening permissions on remote backend files..."
ssh -o ControlPath="$CONTROL_PATH" $USER@$HOST "chmod -R g-w,o-w ${REMOTE_DIR}backend || true; find ${REMOTE_DIR}backend -type f -name '*.cgi' -exec chmod 755 {} \; -o -name '*.py' -exec chmod 644 {} \; || true"
echo "✅ Remote permissions hardened."


# If backend did not exist before, run pip install and init_db.py
if [ "$BACKEND_EXISTS" = "0" ]; then
    echo "🛠️  First-time backend setup: installing dependencies and initializing database..."
    ssh -o ControlPath="$CONTROL_PATH" $USER@$HOST "cd ${REMOTE_DIR}backend && if [ -f requirements.txt ]; then pip3 install --user -r requirements.txt || pip3 install --user Flask Flask-CORS; else pip3 install --user Flask Flask-CORS; fi && if [ -f init_db.py ]; then python3 init_db.py; fi"
    echo "✅ Backend initialized."
fi

# Always ensure correct permissions for database directory and file
echo "🔑 Setting permissions for database directory and app.db..."
ssh -o ControlPath="$CONTROL_PATH" $USER@$HOST "chmod 775 ${REMOTE_DIR}backend/database || true"
ssh -o ControlPath="$CONTROL_PATH" $USER@$HOST "chmod 664 ${REMOTE_DIR}backend/database/app.db || true"
echo "✅ Permissions set."

echo ""
echo "🔧 Setting CGI permissions..."
ssh -o ControlPath="$CONTROL_PATH" $USER@$HOST "if [ -f ${REMOTE_DIR}backend/api.cgi ]; then chmod 755 ${REMOTE_DIR}backend/api.cgi || true; fi"
ssh -o ControlPath="$CONTROL_PATH" $USER@$HOST "if [ -f ${REMOTE_DIR}backend/.htaccess ]; then chmod 644 ${REMOTE_DIR}backend/.htaccess || true; fi"


# Ensure remote backend logs directory exists (but do not overwrite or touch log files)
echo "\n📝 Ensuring remote backend/logs/ directory exists (logs not overwritten)..."
ssh -o ControlPath="$CONTROL_PATH" $USER@$HOST "mkdir -p ${REMOTE_DIR}backend/logs && chmod 755 ${REMOTE_DIR}backend/logs || true"
# Create default log files only if they do not already exist (do not overwrite existing logs)
ssh -o ControlPath="$CONTROL_PATH" $USER@$HOST "for f in flask_error.log cgi_error.log import_time.log nosebeep_api_logs.txt; do if [ ! -f ${REMOTE_DIR}backend/logs/\$f ]; then touch ${REMOTE_DIR}backend/logs/\$f && chmod 664 ${REMOTE_DIR}backend/logs/\$f || true; fi; done"
echo "✅ Remote logs directory ensured (existing logs preserved)."

echo ""
echo "📦 Deploying frontend source to ${REMOTE_DIR}frontend/..."
rsync -avz --progress \
    -e "ssh -o ControlPath=$CONTROL_PATH" \
    --exclude='node_modules/' \
    --exclude='dist/' \
    --exclude='dist-ssr/' \
    --exclude='.git/' \
    --exclude='.DS_Store' \
    --exclude='*.local' \
    frontend/ $USER@$HOST:${REMOTE_DIR}frontend/

echo ""
echo "\n🏗️  Deploying built frontend to $REMOTE_DIR (web root)..."
echo "🔁 Generating frontend config and building frontend locally (to populate frontend/dist)"
# Generate config for frontend (ensures BASE_URL matches config.json)
node frontend/generate-config.js

# Install frontend deps if missing (fast path)
if [ ! -d "frontend/node_modules" ]; then
    echo "📥 Installing frontend dependencies (first-time)..."
    (cd frontend && npm install)
fi

echo "🏗 Building frontend..."
if (cd frontend && npm run build); then
    echo "✅ Frontend built. Deploying dist to $REMOTE_DIR"
    rsync -avz --progress \
        -e "ssh -o ControlPath=$CONTROL_PATH" \
        frontend/dist/ $USER@$HOST:$REMOTE_DIR/
    echo "✅ Frontend deployed to $REMOTE_DIR"
else
    echo "⚠️  Frontend build failed — skipping dist deploy"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "All files deployed to: $REMOTE_DIR"
DOMAIN=$(grep -o '"domain": *"[^"]*"' config.json | cut -d'"' -f4)
# Ensure we print HTTP URLs for the CGI endpoints (convert https -> http if present)
DOMAIN_HTTP="${DOMAIN/#https:\/\//http://}"
if [ -z "$SUB_DIR" ]; then
    echo "Web root: $DOMAIN_HTTP/"
    echo "Backend API: $DOMAIN_HTTP/backend/api.cgi/"
else
    echo "Web root: $DOMAIN_HTTP/$SUB_DIR"
    echo "Backend API: $DOMAIN_HTTP/${SUB_DIR}backend/api.cgi/"
fi
