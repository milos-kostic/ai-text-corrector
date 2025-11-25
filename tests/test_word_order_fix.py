# test_word_order_fix.py
import requests


def test_word_order():
    tests = [
        ("yesterday i go to store", "Yesterday I went to store"),  # ✅ OVO JE ISPRAVNO
        ("always he is late", "He always is late"),
        ("i tomorrow will go", "I will go tomorrow"),
    ]

    for input_text, expected in tests:
        response = requests.post("http://127.0.0.1:5000/correct", json={"text": input_text})
        actual = response.json().get("corrected", "")
        passed = actual.strip() == expected.strip()
        print(f"{'✅' if passed else '❌'} '{input_text}' → '{actual}'")
        if not passed:
            print(f"   Expected: '{expected}'")


if __name__ == "__main__":
    test_word_order()