"""
simple_error_handler.py
=======================
KISS principle: Simple error handling that's good enough for production
"""

import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
from flask import request, jsonify
import time
import os


def setup_simple_logging():
    """One log file. Clean, readable, no emojis."""

    os.makedirs('logs', exist_ok=True)

    # File handler - always UTF-8
    handler = RotatingFileHandler(
        'logs/api.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()  # Avoid duplicate handlers in reloads
    logger.addHandler(handler)
    logger.addHandler(console)

    logging.info("Logging initialized successfully")  # bez emojija


def handle_errors(f):
    """Simple error decorator - catches everything"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()

        try:
            result = f(*args, **kwargs)

            duration = (time.time() - start) * 1000
            if duration > 1000:
                logging.warning(f"SLOW REQUEST: {request.endpoint} took {duration:.0f}ms")

            return result

        except ValueError as e:
            logging.warning(f"Validation error in {request.endpoint}: {str(e)}")
            return jsonify({"error": str(e), "status": "error"}), 400

        except Exception as e:
            logging.error(f"UNHANDLED ERROR in {request.endpoint}: {str(e)}", exc_info=True)
            return jsonify({
                "error": "Internal server error",
                "status": "error"
            }), 500

    return wrapper


def validate_request():
    """Validate incoming JSON request"""
    if not request.is_json:
        raise ValueError("Request must be JSON")

    data = request.get_json()
    if not data or 'text' not in data:
        raise ValueError("Missing 'text' field in JSON")

    text = data['text']
    if not isinstance(text, str):
        raise ValueError("'text' must be a string")

    if len(text) > 50000:
        raise ValueError("Text too long (max 50,000 characters)")

    return text.strip()