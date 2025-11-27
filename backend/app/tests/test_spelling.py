import requests
import json
import time
from datetime import datetime

API_URL = "http://127.0.0.1:5000/correct/spelling"
OUTPUT_FILE = "TEST_SPELLING_RESULTS.txt"


# =============================
# Helper – normalizacija rezultata
# =============================
def normalize(s: str) -> str:
    """
    Normalizuje string tako da se poredi case-insensitive,
    bez početnih/trailing space-ova.
    """
    if not isinstance(s, str):
        return ""
    return s.strip().lower()


# =============================
# Spelling test set
# NOTE: Removed "their" and "your" - these are now handled by contextual_corrector
# =============================
SPELLING_TESTS = [
    ("teh", "the"),
    ("adress", "address"),
    ("recieve", "receive"),
    ("occurence", "occurrence"),
    ("accomodate", "accommodate"),
    ("definately", "definitely"),
    ("seperate", "separate"),
    ("wich", "which"),
    ("becuase", "because"),
    ("alot", "a lot"),
    ("truely", "truly"),
    ("goverment", "government"),
    ("enviroment", "environment"),
    ("untill", "until"),
    ("wiches", "which"),
    # REMOVED: ("their", "there") - now in contextual_corrector
    # REMOVED: ("your", "you're") - now in contextual_corrector
]

CAPITALIZATION_TESTS = [
    ("Teh", "The"),
    ("TEH", "THE"),
    ("Recieve", "Receive"),
    ("GOVERMENT", "GOVERNMENT"),
]

SENTENCE_TESTS = [
    ("I definately adress teh problem", "I definitely address the problem"),
    # REMOVED: ("Your goverment recieve alot", ...) - "Your" is contextual
    ("Wich occurence is truely bad", "Which occurrence is truly bad"),
]


# =============================
# API poziv
# =============================
def request_api(text):
    start = time.time()
    try:
        r = requests.post(API_URL, json={"text": text}, timeout=10)
        ms = round((time.time() - start) * 1000, 2)

        if r.status_code != 200:
            return None, ms, f"HTTP {r.status_code}: {r.text}"

        return r.json().get("corrected", ""), ms, None

    except Exception as e:
        return None, 0, str(e)


# =============================
# Pojedinačan test
# =============================
def run_single_test(name, wrong, expected):
    actual, response_time, error = request_api(wrong)

    if error:
        return {
            "test": name,
            "input": wrong,
            "expected": expected,
            "actual": error,
            "passed": False,
            "response_time": response_time,
        }

    passed = normalize(actual) == normalize(expected)

    return {
        "test": name,
        "input": wrong,
        "expected": expected,
        "actual": actual,
        "passed": passed,
        "response_time": response_time,
    }


# =============================
# Upis rezultata
# =============================
def save_results(results):
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    success_rate = round((passed / total) * 100, 2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== SPELLING TEST RESULTS - {datetime.now()} ===\n")
        f.write(f"TOTAL: {total} | PASSED: {passed} | SUCCESS: {success_rate}%\n\n")
        f.write("NOTE: Contextual homophones (their/your) are tested in test_contextual_spelling.py\n\n")

        for r in results:
            line = json.dumps(r, ensure_ascii=False)
            f.write(line + "\n")

    print(f"\n📄 Rezultati upisani u {OUTPUT_FILE}")
    print(f"🎯 SUCCESS RATE: {success_rate}%\n")


# =============================
# MAIN
# =============================
def main():
    results = []

    print("\n=== RUNNING SPELLING TESTS ===\n")

    # Direktna pravila spelling correctora
    for wrong, expected in SPELLING_TESTS:
        name = f"Rule: {wrong} → {expected}"
        r = run_single_test(name, wrong, expected)
        results.append(r)
        print(("✓" if r["passed"] else "✗"), name)

    # Testovi kapitalizacije
    print("\n=== CAPITALIZATION TESTS ===")
    for wrong, expected in CAPITALIZATION_TESTS:
        name = f"Caps: {wrong}"
        r = run_single_test(name, wrong, expected)
        results.append(r)
        print(("✓" if r["passed"] else "✗"), name)

    # Testovi rečenica
    print("\n=== SENTENCE TESTS ===")
    for wrong, expected in SENTENCE_TESTS:
        name = "Sentence"
        r = run_single_test(name, wrong, expected)
        results.append(r)
        print(("✓" if r["passed"] else "✗"), wrong)

    save_results(results)
    print("✅ DONE\n")
    print("💡 TIP: For contextual spelling (their/your), run: python test_contextual_spelling.py\n")


if __name__ == "__main__":
    main()