CGI wrapper (`api.cgi`) — how to add a CGI script (clean)

Follow these exact steps to add a new CGI script whose exceptions are
recorded in `backend/cgi_error.log` via the `api.cgi` wrapper.

1) Create the script in `backend/`
CGI wrapper (`api.cgi`) — how to add a CGI script (clean)

Follow these exact steps to add a new CGI script whose exceptions are
recorded in `backend/cgi_error.log` via the `api.cgi` wrapper.

1) Create the script in `backend/`

   - File: `backend/my_script.py`
   - Script must output HTTP headers first, then the body.

     ```python
     # backend/my_script.py
     print('Content-Type: text/plain')
     print()
     print('Hello from my_script')
     ```

2) Log exceptions to `cgi_error.log`

   - Import `logging_helper` and call `logging_helper.log_exception()` in
     `except` blocks to append tracebacks:

     ```python
     import logging_helper

     try:
         # do work
     except Exception:
         logging_helper.log_exception()
         raise
     ```

3) Run via the wrapper (`WRAPPED_SCRIPT`)

   - Set `WRAPPED_SCRIPT` to the script path relative to `backend/`.

   - `.htaccess` example (in `backend/`):

     ```apache
     SetEnv WRAPPED_SCRIPT my_script.py
     Options +ExecCGI
     AddHandler cgi-script .cgi
     ```

   - Local test:

     ```bash
     cd backend
     WRAPPED_SCRIPT=my_script.py ./api.cgi
     ```

4) Permissions & deploy

   - Ensure `api.cgi` is executable: `chmod 755 backend/api.cgi`.
   - `deploy.sh` ensures `backend/cgi_error.log` exists and is writable by group.

5) Test & inspect logs

   - Local test harness: `cd backend && ./test-cgi.sh`.
   - Inspect wrapper log: `tail -n 200 backend/cgi_error.log`.
   - To show tracebacks in the browser temporarily set `DEBUG=1`.

Notes

   - Use only relative `WRAPPED_SCRIPT` values inside `backend/`.
   - `api.cgi` sets `APP_BASE_DIR` so scripts can find `database/`.
