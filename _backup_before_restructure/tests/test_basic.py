import requests
import json
import time
from datetime import datetime

API_URL = "http://127.0.0.1:5000/correct"
OUTPUT_FILE = "TEST_BASIC_RESULTS.txt"


def request_api(text):
    """Poziva /correct endpoint i meri vreme."""
    start = time.time()
    try:
        r = requests.post(API_URL, json={"text": text})
        ms = round((time.time() - start) * 1000, 2)

        if r.status_code != 200:
            return None, ms, f"HTTP {r.status_code}: {r.text}"

        data = r.json()
        return data.get("corrected", ""), ms, None

    except Exception as e:
        return None, 0, str(e)


def run_test(name, input_text, expected):
    """Izvršava jedan test slučaj."""
    actual, rt, error = request_api(input_text)

    if error:
        return {
            "test": name,
            "input": input_text,
            "expected": expected,
            "actual": error,
            "passed": False,
            "response_time": rt
        }

    return {
        "test": name,
        "input": input_text,
        "expected": expected,
        "actual": actual,
        "passed": actual.strip() == expected.strip(),
        "response_time": rt
    }


def save_results(results):
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    success_rate = round((passed / total) * 100, 2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== BASIC TEST RESULTS - {datetime.now()} ===\n")
        f.write(f"TOTAL: {total} | PASSED: {passed} | SUCCESS: {success_rate}%\n\n")

        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\n📄 Rezultati upisani u {OUTPUT_FILE}")
    print(f"🎯 SUCCESS RATE: {success_rate}%\n")


def main():
    results = []

    print("\n=== RUNNING BASIC TESTS ===\n")

    # Sekcija 1 — BASIC input cleanup
    BASIC_TESTS = [
        ("Whitespace normalization", "Hello     world", "Hello world"),
        ("Tabs to single space", "Hello\t\tworld", "Hello world"),
        ("Newline collapse", "Hello\n\nworld", "Hello world"),
        ("Trim spaces", "   hello world   ", "Hello world"),
        ("Zero-width removal", "he\u200bllo wor\u200bld", "Hello world"),
    ]

    # Sekcija 2 — Capitalization
    CAPITALIZATION_TESTS = [
        ("Sentence capitalization", "hello world. this is test", "Hello world. This is test"),
        ("Single sentence cap", "hello there", "Hello there"),
        ("All caps fix", "THIS IS TEXT", "This is text"),
        ("Random casing", "hElLo WoRLD", "Hello world"),
    ]

    # Sekcija 3 — Punctuation
    PUNCT_TESTS = [
        ("Fix double period", "Hello.. world", "Hello. world"),
        ("Fix missing space", "Hello,world", "Hello, world"),
        ("Fix repeated punctuation", "Hello!!! world??", "Hello! world?"),
        ("Normalize apostrophes", "It's fine", "It's fine"),  # AŽURIRANO: sada će raditi
        ("Normalize smart quotes", "It's working", "It's working"),  # NOVI TEST
        ("Normalize malformed UTF-8", "Itâ€™s fixed", "It's fixed"),  # NOVI TEST
    ]

    # Sekcija 4 — Preservation (things that must NOT break)
    PRESERVE_TESTS = [
        ("Preserve URL", "visit https://google.com now", "Visit https://google.com now"),
        ("Preserve email", "contact me at test@example.com", "Contact me at test@example.com"),
        ("Preserve hashtag", "follow #python now", "Follow #python now"),
        ("Preserve mention", "talk to @admin now", "Talk to @admin now"),
    ]

    # Sekcija 5 — Realistic grammar and spelling
    REALISTIC_TESTS = [
        ("Simple spelling", "I beleive this is corect", "I believe this is correct"),
        ("Grammar error", "this are bad sentence", "This is a bad sentence"),
        ("Mixed casing + typo", "thIS is terrble", "This is terrible"),
    ]

    # Sekcija 6 — Edge cases
    EDGE_TESTS = [
        ("Empty string", "", ""),
        ("Only spaces", "     ", ""),
        ("Numbers preserved", "price is 123$", "Price is 123$"),
        ("Emoji preservation", "hello 😃 world", "Hello 😃 world"),
    ]

    # Sekcija 7 — Regression tests
    REGRESSION_TESTS = [
        ("Already correct", "Hello world.", "Hello world."),
        ("Complex punctuation", "this is. a test.. ok?", "This is. A test. Ok?"),
    ]

    ALL = [
        ("BASIC", BASIC_TESTS),
        ("CAPITALIZATION", CAPITALIZATION_TESTS),
        ("PUNCTUATION", PUNCT_TESTS),
        ("PRESERVE", PRESERVE_TESTS),
        ("REALISTIC", REALISTIC_TESTS),
        ("EDGE CASES", EDGE_TESTS),
        ("REGRESSION", REGRESSION_TESTS),
    ]

    for section_name, tests in ALL:
        print(f"\n=== {section_name} ===")
        for name, inp, exp in tests:
            r = run_test(name, inp, exp)
            results.append(r)
            print(("✓" if r["passed"] else "✗"), name)

    save_results(results)


if __name__ == "__main__":
    main()