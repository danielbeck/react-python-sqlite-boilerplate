#!/bin/bash
# Test script for CGI on the server

echo "Testing CGI with proper environment..."

# Simulate a GET request to the correct endpoint
REQUEST_METHOD=GET \
PATH_INFO=/items \
SCRIPT_NAME=/backend/api.cgi \
SERVER_NAME=localhost \
SERVER_PORT=80 \
./api.cgi

echo ""
echo "---"
echo "If you see JSON output above, the CGI script works!"
echo "Now test via browser: http://nosebeep.com/backend/api.cgi/items"
