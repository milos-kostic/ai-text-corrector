from functools import wraps
from flask import request, jsonify
import os

# Minimalna verzija za MVP — ključevi iz .env
VALID_API_KEYS = {
    "basic": os.getenv("API_KEY_BASIC", "basic_key_123"),
    "premium": os.getenv("API_KEY_PREMIUM", "premium_key_456"),
    "enterprise": os.getenv("API_KEY_ENTERPRISE", "enterprise_key_789"),
}

def require_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return jsonify({"error": "API key required"}), 401

        plan = None
        for p, key in VALID_API_KEYS.items():
            if api_key == key:
                plan = p
                break

        if not plan:
            return jsonify({"error": "Invalid API key"}), 401

        request.current_plan = plan
        return f(*args, **kwargs)

    return wrapper
