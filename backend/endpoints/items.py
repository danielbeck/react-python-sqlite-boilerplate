from flask import Blueprint, jsonify, request, current_app

bp = Blueprint('items', __name__, url_prefix='/items')

def get_db():
    # Import from app context
    return current_app.config['get_db']()

def dict_from_row(row):
    return current_app.config['dict_from_row'](row)

@bp.route('/', methods=['GET'])
def get_items():
    conn = get_db()
    items = conn.execute('SELECT * FROM items ORDER BY id').fetchall()
    conn.close()
    return jsonify({'items': [dict_from_row(i) for i in items]})

@bp.route('/', methods=['POST'])
def create_item():
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

@bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    conn = get_db()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    if item:
        return jsonify({'item': dict_from_row(item)})
    return jsonify({'error': 'Item not found'}), 404

@bp.route('/<int:item_id>', methods=['PUT'])
def update_item(item_id):
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

@bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item deleted'})
