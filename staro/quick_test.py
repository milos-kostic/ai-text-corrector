# quick_test.py - Za brzu proveru osnovnih funkcionalnosti
import requests


def quick_test():
    """Brzi test osnovnih funkcionalnosti"""
    test_cases = [
        ("teh quick brown fox", "the quick brown fox"),
        ("he have a car", "he has a car"),
        ("she dont like", "she doesn't like"),
        ("we was there", "we were there"),
        ("I is happy", "I am happy"),
    ]

    print("🚀 QUICK FUNCTIONALITY TEST")
    print("=" * 50)

    for input_text, expected in test_cases:
        try:
            response = requests.post(
                "http://localhost:5000/correct",
                json={"text": input_text},
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                actual = result['corrected_text']
                status = "✅" if actual.lower() == expected.lower() else "❌"
                print(f"{status} '{input_text}' -> '{actual}' (expected: '{expected}')")
            else:
                print(f"❌ '{input_text}' -> HTTP {response.status_code}")

        except Exception as e:
            print(f"💥 '{input_text}' -> Error: {e}")


if __name__ == "__main__":
    quick_test()