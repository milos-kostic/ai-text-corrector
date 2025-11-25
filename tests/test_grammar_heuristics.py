"""
test_grammar_heuristics.py
===========================
Targeted test for specific grammar rules:
1. is/are agreement (this/that/these/those)
2. Missing articles (a/an before adjective+noun)

Quick test to verify these mini-heuristics work.
"""

import requests
import json
from datetime import datetime

API_URL = "http://127.0.0.1:5000/correct"


def test_correction(input_text, expected_output, description):
    """Test single correction"""
    try:
        r = requests.post(API_URL, json={"text": input_text}, timeout=5)

        if r.status_code != 200:
            return {
                "description": description,
                "input": input_text,
                "expected": expected_output,
                "actual": f"ERROR {r.status_code}",
                "passed": False
            }

        actual = r.json().get("corrected", "")
        passed = actual.strip() == expected_output.strip()

        return {
            "description": description,
            "input": input_text,
            "expected": expected_output,
            "actual": actual,
            "passed": passed
        }

    except Exception as e:
        return {
            "description": description,
            "input": input_text,
            "expected": expected_output,
            "actual": f"EXCEPTION: {str(e)}",
            "passed": False
        }


def main():
    print("\n" + "=" * 70)
    print("🔍 GRAMMAR HEURISTICS TEST - is/are & articles")
    print("=" * 70 + "\n")

    results = []

    # ============================================
    # TEST SET 1: is/are with demonstratives
    # ============================================
    print("📌 Test 1: is/are agreement with this/that/these/those\n")

    is_are_tests = [
        # this/that (singular) + is
        ("this are wrong", "This is wrong", "this + are → this + is"),
        ("that are correct", "That is correct", "that + are → that + is"),
        ("this were bad", "This was bad", "this + were → this + was"),
        ("that were good", "That was good", "that + were → that + was"),

        # these/those (plural) + are
        ("these is wrong", "These are wrong", "these + is → these + are"),
        ("those is correct", "Those are correct", "those + is → those + are"),
        ("these was bad", "These were bad", "these + was → these + were"),
        ("those was good", "Those were good", "those + was → those + were"),
    ]

    for inp, exp, desc in is_are_tests:
        result = test_correction(inp, exp, desc)
        results.append(result)
        status = "✅" if result["passed"] else "❌"
        print(f"{status} {desc}")
        if not result["passed"]:
            print(f"   Input:    '{inp}'")
            print(f"   Expected: '{exp}'")
            print(f"   Actual:   '{result['actual']}'")
        print()

    # ============================================
    # TEST SET 2: Missing articles (a/an)
    # ============================================
    print("\n📌 Test 2: Missing articles before adjective + noun\n")

    article_tests = [
        # is + adjective + noun (missing "a")
        ("this is bad sentence", "This is a bad sentence", "is + bad sentence → is a bad sentence"),
        ("that is good idea", "That is a good idea", "is + good idea → is a good idea"),
        ("it is big problem", "It is a big problem", "is + big problem → is a big problem"),

        # was + adjective + noun (missing "a")
        ("this was bad sentence", "This was a bad sentence", "was + bad sentence → was a bad sentence"),
        ("it was good idea", "It was a good idea", "was + good idea → was a good idea"),

        # Vowel sounds - should add "an"
        ("this is important issue", "This is an important issue", "is + important → is an important"),
        ("that was easy task", "That was an easy task", "was + easy → was an easy"),
    ]

    for inp, exp, desc in article_tests:
        result = test_correction(inp, exp, desc)
        results.append(result)
        status = "✅" if result["passed"] else "❌"
        print(f"{status} {desc}")
        if not result["passed"]:
            print(f"   Input:    '{inp}'")
            print(f"   Expected: '{exp}'")
            print(f"   Actual:   '{result['actual']}'")
        print()

    # ============================================
    # TEST SET 3: Combined patterns
    # ============================================
    print("\n📌 Test 3: Combined corrections\n")

    combined_tests = [
        # is/are + missing article
        ("this are bad sentence", "This is a bad sentence", "this are → this is + add 'a'"),
        ("these is good idea", "These are a good idea", "these is → these are + add 'a'"),

        # Real user mistakes
        ("this are terrible mistake", "This is a terrible mistake", "Real mistake: this are + no article"),
    ]

    for inp, exp, desc in combined_tests:
        result = test_correction(inp, exp, desc)
        results.append(result)
        status = "✅" if result["passed"] else "❌"
        print(f"{status} {desc}")
        if not result["passed"]:
            print(f"   Input:    '{inp}'")
            print(f"   Expected: '{exp}'")
            print(f"   Actual:   '{result['actual']}'")
        print()

    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "=" * 70)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    success_rate = round((passed / total) * 100, 2)

    print(f"📊 RESULTS: {passed}/{total} passed ({success_rate}%)")

    # Break down by category
    is_are_passed = sum(1 for r in results[:8] if r["passed"])
    article_passed = sum(1 for r in results[8:15] if r["passed"])
    combined_passed = sum(1 for r in results[15:] if r["passed"])

    print(f"\n   is/are agreement: {is_are_passed}/8")
    print(f"   Missing articles: {article_passed}/7")
    print(f"   Combined: {combined_passed}/3")

    print("\n" + "=" * 70)

    if success_rate == 100:
        print("✅ ALL HEURISTICS WORKING PERFECTLY")
    elif success_rate >= 80:
        print("⚠️  MOST HEURISTICS WORK - Some edge cases need fixing")
    else:
        print("❌ HEURISTICS NEED WORK")

    print("=" * 70 + "\n")

    # Save detailed results
    with open("GRAMMAR_HEURISTICS_TEST.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "success_rate": success_rate,
                "by_category": {
                    "is_are_agreement": f"{is_are_passed}/8",
                    "missing_articles": f"{article_passed}/7",
                    "combined": f"{combined_passed}/3"
                }
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print("💾 Detailed results saved to: GRAMMAR_HEURISTICS_TEST.json\n")


if __name__ == "__main__":
    try:
        # Quick health check
        r = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if r.status_code != 200:
            print("❌ Server not healthy")
            exit(1)
    except:
        print("❌ Server not running at http://127.0.0.1:5000")
        print("Start it with: python app.py")
        exit(1)

    main()