# backend/run.py
from app.main import app

if __name__ == '__main__':
    print("AI Text Corrector API pokrenut na http://0.0.0.0:5000")
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)