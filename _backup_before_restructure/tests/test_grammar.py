import requests
import json
import time
from datetime import datetime

API_URL = "http://127.0.0.1:5000/correct/grammar"
OUTPUT_FILE = "TEST_GRAMMAR_RESULTS.txt"


def beep():
    try:
        print("\a", end="")  # mali bip u terminalu
    except:
        pass


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


def run_test(name, input_text, expected):
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
        f.write(f"=== GRAMMAR TEST RESULTS - {datetime.now()} ===\n")
        f.write(f"TOTAL: {total} | PASSED: {passed} | SUCCESS: {success_rate}%\n\n")

        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

        f.write("\n======== MVP STATUS ========\n")
        if success_rate >= 60:
            f.write("✅ ACCEPTABLE FOR MVP\n")
        else:
            f.write("❌ BELOW MVP QUALITY THRESHOLD\n")

    print(f"\n📄 Rezultati upisani u {OUTPUT_FILE}")
    print(f"🎯 GRAMMAR SCORE: {success_rate}%")

    if success_rate >= 60:
        print("✅ STATUS: ACCEPTABLE FOR MVP\n")
    else:
        print("❌ STATUS: BELOW MVP QUALITY\n")

    beep()


def main():
    results = []

    print("\n=== RUNNING GRAMMAR TESTS ===\n")

    TESTS = [

        # --- VERB AGREEMENT ---
        ("Verb agreement he", "he go to school", "He goes to school"),
        ("Verb agreement she", "she have a car", "She has a car"),
        ("Verb agreement I", "i is happy", "I am happy"),

        # --- IRREGULAR VERBS ---
        ("Irregular past", "she didn't ate dinner", "She didn't eat dinner"),
        ("Irregular correction", "he goed home", "He went home"),
        ("Perfect tense", "he has ate", "He has eaten"),

        # --- ARTICLES ---
        ("Article vowel", "a umbrella is here", "An umbrella is here"),
        ("Article consonant", "an book is missing", "A book is missing"),

        # --- COMMON USER CHAT ---
        ("User phrase 1", "i dont understand this system", "I don't understand this system"),
        ("User phrase 2", "why she dont reply me", "Why doesn't she reply me"),
        ("User phrase 3", "me and him was late", "He and I were late"),

        # --- WORD ORDER ---
        ("Word order", "always he is late", "He always is late"),

        # --- PREPOSITIONS ---
        ("Preposition error", "he arrived to airport", "He arrived at airport"),

        # --- REALISTIC MIX ---
        ("Complex sentence",
         "he dont know where she was went yesterday",
         "He doesn't know where she went yesterday"),
    ]

    for name, inp, exp in TESTS:
        r = run_test(name, inp, exp)
        results.append(r)
        print(("✓" if r["passed"] else "✗"), name)

    save_results(results)


if __name__ == "__main__":
    main()
