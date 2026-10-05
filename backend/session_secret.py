import json
import os

from dotenv import dotenv_values


def load_session_secret():
    secret_file = os.environ.get('APP_SECRET_FILE')
    if secret_file:
        with open(secret_file) as source:
            settings = json.load(source)
        key = settings.get('SECRET_KEY') if isinstance(settings, dict) else None
    else:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        key = os.environ.get('SECRET_KEY') or dotenv_values(env_file, interpolate=False).get('SECRET_KEY')
    if not isinstance(key, str) or not key.strip():
        raise ValueError('SECRET_KEY is required in the environment, local .env, or private server configuration.')
    return key
