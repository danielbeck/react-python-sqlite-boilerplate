from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import logging
import traceback
from collections import deque

app = Flask(__name__)
CORS(app)

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

# ============ ITEMS ENDPOINTS ============

@app.route('/items', methods=['GET'])
def get_items():
    """Get all items"""
    conn = get_db()
    items = conn.execute('SELECT * FROM items ORDER BY id').fetchall()
    conn.close()
    return jsonify({'items': [dict_from_row(i) for i in items]})




@app.route('/items', methods=['POST'])
def create_item():
    """Create a new item"""
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO items (name, description)
        VALUES (?, ?)
    ''', (data['name'], data.get('description', '')))
    
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': item_id, 'message': 'Item created'}), 201

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get a specific item"""
    conn = get_db()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    
    if item:
        return jsonify({'item': dict_from_row(item)})
    return jsonify({'error': 'Item not found'}), 404

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Update an item"""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    if 'name' in data:
        fields.append('name = ?')
        values.append(data['name'])
    
    if 'description' in data:
        fields.append('description = ?')
        values.append(data['description'])
    
    if not fields:
        conn.close()
        return jsonify({'error': 'No fields to update'}), 400
    
    fields.append('updated_at = CURRENT_TIMESTAMP')
    values.append(item_id)
    
    cursor.execute(f"UPDATE items SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Item updated'})

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an item"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Item deleted'})


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
