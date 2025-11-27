import requests
import json
from datetime import datetime
import sys

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://127.0.0.1:5000/correct"
OUTPUT_FILE = "TEST_CONTEXTUAL_RESULTS.txt"


def test_correction(text):
    """Test single correction and return result"""
    try:
        r = requests.post(API_URL, json={"text": text}, timeout=10)
        if r.status_code == 200:
            return r.json().get("corrected", "")
        return f"ERROR: {r.status_code}"
    except Exception as e:
        return f"ERROR: {str(e)}"


def main():
    print("\n=== TESTING CONTEXTUAL SPELLING ===\n")

    # Test cases: (input, expected_correct, description)
    tests = [
        # THEIR/THERE/THEY'RE tests
        ("this is their car", "This is their car", "THEIR (possessive + noun) - should stay 'their'"),
        ("their going to school", "They're going to school", "THEIR → THEY'RE (before verb)"),
        ("there is a problem", "There is a problem", "THERE (location/existential) - should stay 'there'"),
        ("over there by the tree", "Over there by the tree", "THERE (location) - should stay 'there'"),
        ("they're happy today", "They're happy today", "THEY'RE (contraction) - should stay 'they're'"),

        # YOUR/YOU'RE tests
        ("this is your book", "This is your book", "YOUR (possessive + noun) - should stay 'your'"),
        ("your going to like this", "You're going to like this", "YOUR → YOU'RE (before verb)"),
        ("you're awesome", "You're awesome", "YOU'RE (contraction) - should stay 'you're'"),
        ("take your time", "Take your time", "YOUR (possessive) - should stay 'your'"),

        # Edge cases
        ("their happy", "They're happy", "THEIR → THEY'RE (before adjective)"),
        ("your welcome", "You're welcome", "YOUR → YOU'RE (set phrase)"),
    ]

    results = []
    passed = 0
    failed = 0

    for input_text, expected, description in tests:
        actual = test_correction(input_text)
        is_correct = actual.strip() == expected.strip()

        if is_correct:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"

        result = {
            "status": status,
            "description": description,
            "input": input_text,
            "expected": expected,
            "actual": actual,
            "correct": is_correct
        }

        results.append(result)
        print(f"{status} | {description}")
        if not is_correct:
            print(f"         Input:    '{input_text}'")
            print(f"         Expected: '{expected}'")
            print(f"         Actual:   '{actual}'")
        print()

    # Save results
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"=== CONTEXTUAL SPELLING TEST - {datetime.now()} ===\n")
            f.write(f"PASSED: {passed} | FAILED: {failed} | TOTAL: {len(tests)}\n")
            f.write(f"SUCCESS RATE: {round(passed / len(tests) * 100, 2)}%\n\n")

            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        print(f"\n📊 RESULTS: {passed}/{len(tests)} passed ({round(passed / len(tests) * 100, 2)}%)")
        print(f"📄 Details saved to: {OUTPUT_FILE}\n")
    except Exception as e:
        print(f"\n❌ ERROR saving results: {e}\n")


if __name__ == "__main__":
    main()