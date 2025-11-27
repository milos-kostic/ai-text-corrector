"""
app.py - AI Text Corrector API
================================
Clean, fast, production-ready. No emojis in logs.
"""

from flask import Flask, request, jsonify
import logging
from simple_error_handler import setup_simple_logging, handle_errors, validate_request

from correctors.spelling_corrector import SpellingCorrector
from correctors.grammar_corrector import GrammarCorrector

app = Flask(__name__)

# Setup logging (clean)
setup_simple_logging()
logger = logging.getLogger(__name__)

# Initialize correctors
try:
    spelling_corrector = SpellingCorrector()
    grammar_corrector = GrammarCorrector()
    logger.info("Correctors loaded successfully")
except Exception as e:
    logger.critical(f"Failed to load correctors: {e}")
    spelling_corrector = None
    grammar_corrector = None


@app.route('/')
def home():
    return jsonify({
        'service': 'AI Text Corrector API',
        'version': '1.4.0',
        'status': 'running',
        'endpoints': ['/correct', '/correct/spelling', '/correct/grammar', '/correct/batch', '/health']
    })


@app.route('/correct', methods=['POST'])
@handle_errors
def correct_all():
    text = validate_request()
    if not text:
        return jsonify({"original": "", "corrected": "", "changed": False})

    corrected = grammar_corrector.correct(text)

    return jsonify({
        "original": text,
        "corrected": corrected,
        "changed": corrected != text
    })


@app.route('/correct/spelling', methods=['POST'])
@handle_errors
def correct_spelling():
    text = validate_request()
    if not text:
        return jsonify({"original": "", "corrected": "", "changed": False})

    corrected = spelling_corrector.correct(text)

    return jsonify({
        "original": text,
        "corrected": corrected,
        "changed": corrected != text
    })


@app.route('/correct/grammar', methods=['POST'])
@handle_errors
def correct_grammar():
    text = validate_request()
    if not text:
        return jsonify({"original": "", "corrected": "", "changed": False})

    corrected = grammar_corrector.correct(text)

    return jsonify({
        "original": text,
        "corrected": corrected,
        "changed": corrected != text
    })


@app.route('/correct/batch', methods=['POST'])
@handle_errors
def correct_batch():
    if not request.is_json:
        raise ValueError("Request must be JSON")

    data = request.get_json()
    if not data or 'texts' not in data:
        raise ValueError("Missing 'texts' array")

    texts = data['texts']
    if not isinstance(texts, list):
        raise ValueError("'texts' must be an array")
    if len(texts) > 100:
        raise ValueError("Maximum 100 texts per batch")

    results = []
    for text in texts:
        if not isinstance(text, str):
            results.append({"original": text, "corrected": "", "error": "Not a string"})
            continue

        text = text.strip()
        try:
            corrected = grammar_corrector.correct(text)
            results.append({
                "original": text,
                "corrected": corrected,
                "changed": corrected != text
            })
        except Exception as e:
            results.append({"original": text, "corrected": "", "error": str(e)})

    return jsonify({"results": results, "batch_size": len(texts)})


@app.route('/health')
def health():
    ok = spelling_corrector is not None or grammar_corrector is not None
    return jsonify({
        'status': 'healthy' if ok else 'unhealthy',
        'correctors_loaded': ok
    }), 200 if ok else 503


if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Starting AI Text Corrector API server")
    logger.info("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)