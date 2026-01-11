import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'app.db')

def init_database():
    """Initialize the database with tables and sample data"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM items')
    if cursor.fetchone()[0] == 0:
        sample_items = [
            ('Sample Item 1', 'This is a sample description'),
            ('Sample Item 2', 'Another sample item'),
            ('Sample Item 3', 'Yet another one'),
        ]
        cursor.executemany('INSERT INTO items (name, description) VALUES (?, ?)', sample_items)
        print(f"Created {len(sample_items)} sample items")

    conn.commit()
    conn.close()
    print(f"\nDatabase initialized at {DB_PATH}")

if __name__ == '__main__':
    init_database()