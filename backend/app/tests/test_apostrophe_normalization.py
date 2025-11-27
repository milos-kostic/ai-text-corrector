"""
test_apostrophe_normalization.py
================================
Test comprehensive apostrophe and quote normalization.
"""

import requests
import json
from datetime import datetime

API_URL = "http://127.0.0.1:5000/correct"
OUTPUT_FILE = "TEST_APOSTROPHE_RESULTS.txt"


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
    print("\n=== TESTING APOSTROPHE NORMALIZATION ===\n")

    # Test cases: (input, expected_correct, description)
    # Using ACTUAL Unicode characters directly (copy-paste them from character map)
    tests = [
        # Basic apostrophes (should stay the same)
        ("It's fine", "It's fine", "Standard apostrophe - should stay"),
        ("Don't worry", "Don't worry", "Contraction apostrophe - should stay"),

        # Smart quotes and apostrophes - ACTUAL Unicode characters
        ("It's fine", "It's fine", "Smart right single quote → standard"),  # ’
        ("It's fine", "It's fine", "Smart left single quote → standard"),   # ‘
        ("He said 'hello'", "He said 'hello'", "Smart quotes in quotes"),

        # Malformed UTF-8 sequences
        ("Itâ€˜s fine", "It's fine", "Malformed UTF-8 left quote"),
        ("Itâ€™s fine", "It's fine", "Malformed UTF-8 right quote"),
        ("Donâ€˜t worry", "Don't worry", "Malformed UTF-8 in contraction"),

        # Double-encoded UTF-8
        ("ItÃ¢â‚¬Ëœs fine", "It's fine", "Double-encoded left quote"),
        ("ItÃ¢â‚¬â„¢s fine", "It's fine", "Double-encoded right quote"),

        # Alternative mojibake patterns
        ("Itã¢â‚¬ëœs fine", "It's fine", "Mojibake left quote pattern"),
        ("Itã¢â‚¬â\"¢s fine", "It's fine", "Mojibake right quote pattern"),
        ("Userã¢â‚¬â\"¢s data", "User's data", "Mojibake possessive"),
        ("UserÃ¢â‚¬â„¢s data", "User's data", "Double-encoded possessive"),

        # Accent marks used as apostrophes
        ("Don't worry", "Don't worry", "Acute accent → apostrophe"),  # ´
        ("We`ll see", "We'll see", "Grave accent → apostrophe"),

        # Mixed content
        ("Itâ€˜s don't problem", "It's don't problem", "Mixed malformed patterns"),

        # Double quotes normalization
        ("He said \"hello\"", "He said \"hello\"", "Smart double quotes → standard"),  # “
        ("He said \"hello\"", "He said \"hello\"", "Smart double quotes → standard"),  # ”

        # Edge cases
        ("'Single quoted'", "'Single quoted'", "Single quotes at boundaries"),
        ('"Double quoted"', '"Double quoted"', "Double quotes at boundaries"),

        # Real-world examples from testing
        ("Itâ€˜s a testâ€™s result", "It's a test's result", "Multiple malformed apostrophes"),
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
            f.write(f"=== APOSTROPHE NORMALIZATION TEST - {datetime.now()} ===\n")
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