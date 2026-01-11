# Backend README

## Python Flask Backend API

This backend provides a simple REST API for managing items. It's designed to run via CGI on shared hosting.

## Requirements

- Python 3.7 or higher (pre-installed on macOS)
- pip (Python package manager)

## Setup

1. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

2. Initialize the database:
```bash
python3 init_db.py
```

This will create:
- `database/app.db` - SQLite database file
- 3 sample items

3. Start the Flask development server:
```bash
python3 app.py
```
app.py              # Main Flask application with all endpoints
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependenciesration and helper functions
├── init_db.php         # Database initialization script
├── agents.php          # Agent CRUD operations
├── world.php           # World configuration
├── simulate.php        # Simulation engine
├── history.php         # Movement history
└── database/
    └── simulator.db    # SQLite database (created after init)
```

## API Examples

### Get All Items
```bash
curl http://localhost:8000/items
```

### Create New Item
```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"New Item","description":"Optional description"}'
```

### Update Item
```bash
curl -X PUT http://localhost:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Item","description":"New description"}'
```

### Delete Item
```bash
curl -X DELETE http://localhost:8000/items/1
```

## CORS

CORS is enabled using Flask-CORS to allow frontend access from any origin.
