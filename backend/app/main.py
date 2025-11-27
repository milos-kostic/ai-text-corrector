"""
main.py - AI Text Corrector API (Flask aplikacija)
==================================================
Sada je ovo glavni fajl unutar Python paketa `app`
Svi importi su relativni → radi savršeno posle reorganizacije
"""

from flask import Flask, request, jsonify
import logging

# RELATIVNI IMPORTI – obavezni jer smo unutar paketa `app`
from .simple_error_handler import setup_simple_logging, handle_errors, validate_request
from .correctors.spelling_corrector import SpellingCorrector
from .correctors.grammar_corrector import GrammarCorrector

# Kreiraj Flask aplikaciju
app = Flask(__name__)

# Postavi čisto logovanje (bez emojija)
setup_simple_logging()
logger = logging.getLogger(__name__)

# Inicijalizacija korektora
try:
    spelling_corrector = SpellingCorrector()
    grammar_corrector = GrammarCorrector()
    logger.info("All correctors loaded successfully")
except Exception as e:
    logger.critical(f"Failed to initialize correctors: {e}")
    spelling_corrector = None
    grammar_corrector = None


@app.route("/")
def home():
    return jsonify({
        "service": "AI Text Corrector API",
        "version": "1.4.0",
        "status": "running",
        "endpoints": [
            "/correct", "/correct/spelling", "/correct/grammar",
            "/correct/batch", "/health"
        ]
    })


@app.route("/correct", methods=["POST"])
@handle_errors
def correct_all():
    text = validate_request()
    if not text:
        return jsonify({"original": "", "corrected": "", "changed": False})

    if grammar_corrector is None:
        raise RuntimeError("Grammar corrector not available")

    corrected = grammar_corrector.correct(text)

    return jsonify({
        "original": text,
        "corrected": corrected,
        "changed": corrected != text
    })


@app.route("/correct/spelling", methods=["POST"])
@handle_errors
def correct_spelling():
    text = validate_request()
    if not text:
        return jsonify({"original": "", "corrected": "", "changed": False})

    if spelling_corrector is None:
        raise RuntimeError("Spelling corrector not available")

    corrected = spelling_corrector.correct(text)

    return jsonify({
        "original": text,
        "corrected": corrected,
        "changed": corrected != text
    })


@app.route("/correct/grammar", methods=["POST"])
@handle_errors
def correct_grammar():
    text = validate_request()
    if not text:
        return jsonify({"original": "", "corrected": "", "changed": False})

    if grammar_corrector is None:
        raise RuntimeError("Grammar corrector not available")

    corrected = grammar_corrector.correct(text)

    return jsonify({
        "original": text,
        "corrected": corrected,
        "changed": corrected != text
    })


@app.route("/correct/batch", methods=["POST"])
@handle_errors
def correct_batch():
    if not request.is_json:
        raise ValueError("Request must be JSON")

    data = request.get_json()
    if not data or "texts" not in data:
        raise ValueError("Missing 'texts' array in request")

    texts = data["texts"]
    if not isinstance(texts, list):
        raise ValueError("'texts' must be a list")
    if len(texts) > 100:
        raise ValueError("Maximum 100 texts allowed per batch")

    if grammar_corrector is None:
        raise RuntimeError("Grammar corrector not available")

    results = []
    for item in texts:
        if not isinstance(item, str):
            results.append({"original": item, "corrected": "", "error": "Input must be string"})
            continue

        original = item.strip()
        if not original:
            results.append({"original": "", "corrected": "", "changed": False})
            continue

        try:
            corrected = grammar_corrector.correct(original)
            results.append({
                "original": original,
                "corrected": corrected,
                "changed": corrected != original
            })
        except Exception as e:
            results.append({"original": original, "corrected": "", "error": str(e)})

    return jsonify({
        "results": results,
        "batch_size": len(results),
        "timestamp": logging.Formatter("%Y-%m-%d %H:%M:%S").format(logging.LogRecord(
            name="", level=0, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        ).created)
    })


@app.route("/health")
def health():
    correctors_ok = spelling_corrector is not None and grammar_corrector is not None
    return jsonify({
        "status": "healthy" if correctors_ok else "degraded",
        "correctors_loaded": correctors_ok,
        "spelling_corrector": spelling_corrector is not None,
        "grammar_corrector": grammar_corrector is not None
    }), 200 if correctors_ok else 503


# Samo za lokalno pokretanje (u produkciji koristiš run.py + waitress)
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting AI Text Corrector API (development mode)")
    logger.info("Use 'python run.py' for production (Waitress)")
    logger.info("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)