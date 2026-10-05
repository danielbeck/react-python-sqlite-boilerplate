import sqlite3
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import re

bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_db():
    return current_app.config['get_db']()

def validate_username(username):
    """Validate username format and length"""
    if not username or not isinstance(username, str):
        return False, 'Username is required'
    if len(username) < 3:
        return False, 'Username must be at least 3 characters'
    if len(username) > 50:
        return False, 'Username must be less than 50 characters'
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, 'Username can only contain letters, numbers, hyphens, and underscores'
    return True, None

def validate_password(password):
    """Validate password strength"""
    if not password or not isinstance(password, str):
        return False, 'Password is required'
    if len(password) < 8:
        return False, 'Password must be at least 8 characters'
    if len(password) > 128:
        return False, 'Password must be less than 128 characters'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'
    if not re.search(r'[0-9]', password):
        return False, 'Password must contain at least one number'
    return True, None

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    # Validate username
    valid, error = validate_username(username)
    if not valid:
        return jsonify({'error': error}), 400
    
    # Validate password
    valid, error = validate_password(password)
    if not valid:
        return jsonify({'error': error}), 400
    
    db = None
    try:
        db = get_db()
        db.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        db.commit()
        # Auto-login: fetch user id and set session
        user = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if user:
            session['user_id'] = user['id']
            session.permanent = True
        db.close()
        return jsonify({'success': True, 'username': username})
    except sqlite3.IntegrityError:
        if db:
            db.close()
        return jsonify({'error': 'Username already exists'}), 409
    except Exception as e:
        current_app.logger.error(f'Error during registration for username {username}: {str(e)}')
        if db:
            db.close()
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    try:
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session.permanent = True
            return jsonify({'success': True, 'username': username})
        
        # Log failed login attempt
        current_app.logger.warning(f'Failed login attempt for username: {username} from IP: {request.remote_addr}')
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        current_app.logger.error(f'Error during login for username {username}: {str(e)}')
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@bp.route('/me', methods=['GET'])
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'user': None}), 200
    try:
        db = get_db()
        user = db.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
        db.close()
        if user:
            return jsonify({'user': user['username']})
        # User was deleted but session still exists
        session.pop('user_id', None)
        return jsonify({'user': None}), 200
    except Exception as e:
        current_app.logger.error(f'Error fetching user info for user_id {user_id}: {str(e)}')
        return jsonify({'error': 'Failed to fetch user information'}), 500
