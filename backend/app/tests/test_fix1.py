import requests

API_URL = "http://127.0.0.1:5000/correct"

tests = [
    ("Hello.. world", "Hello. world"),        # Dupla tačka bez space
    ("Hello!!! world??", "Hello! world?"),    # Multiple punctuation
    ("this is. a test.. ok?", "This is. A test. ok?"),  # Mixed
]

for inp, expected in tests:
    r = requests.post(API_URL, json={"text": inp})
    actual = r.json()["corrected"]
    status = "✅" if actual == expected else "❌"
    print(f"{status} '{inp}' → '{actual}' (expected: '{expected}')")