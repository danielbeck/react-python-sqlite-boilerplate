#!/usr/bin/env python3
"""
Utility to read deployment configuration from config.json
"""
import json
import os

def get_config():
    """Read and return config.json"""
    # Try to find config.json in the project root (parent of backend/)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(backend_dir), 'config.json')
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to default configuration
        return {
            "deployment": {
                "baseDir": "nb/",
                "subDir": ""
            }
        }

def get_backend_path():
    """Get the full backend path for the server"""
    config = get_config()
    base_dir = config['deployment']['baseDir']
    sub_dir = config['deployment'].get('subDir', '')
    
    if sub_dir:
        return f"/kunden/homepages/29/d557350892/htdocs/{base_dir}{sub_dir}backend"
    else:
        return f"/kunden/homepages/29/d557350892/htdocs/{base_dir}backend"

if __name__ == "__main__":
    print(get_backend_path())
