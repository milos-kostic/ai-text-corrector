import requests

API_URL = "http://127.0.0.1:5000/correct"

tests = [
    ("me and i was there", "I and I were there"),
    ("me and him was late", "He and I were late"),
    ("you and me is happy", "You and I are happy"),
    ("him and me was wrong", "He and I were wrong"),
]

for inp, expected in tests:
    r = requests.post(API_URL, json={"text": inp})
    actual = r.json()["corrected"]
    status = "✅" if actual == expected else "❌"
    print(f"{status} '{inp}'")
    print(f"   Got:      '{actual}'")
    print(f"   Expected: '{expected}'")
    print()