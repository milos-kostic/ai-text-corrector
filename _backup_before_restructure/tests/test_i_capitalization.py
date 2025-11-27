"""
test_i_capitalization.py
=========================
COMPREHENSIVE TEST: lowercase "i" → uppercase "I" correction

English rule: First person pronoun "I" is ALWAYS capitalized.

Extended test coverage:
- Basic standalone "i"
- Contractions (i'm, i'll, i've, i'd)
- Multiple "i" in complex sentences
- "i" with various punctuation
- Edge cases and false positives
- Real user chat patterns
- Performance with long texts
- Contextual challenges
"""

import requests
import json
import time
from datetime import datetime

API_URL = "http://127.0.0.1:5000/correct"


def test_correction(input_text, expected_output, description):
    """Test single correction with timing"""
    start_time = time.time()
    try:
        r = requests.post(API_URL, json={"text": input_text}, timeout=10)

        if r.status_code != 200:
            return {
                "description": description,
                "input": input_text,
                "expected": expected_output,
                "actual": f"ERROR {r.status_code}: {r.text}",
                "passed": False,
                "response_time": round((time.time() - start_time) * 1000, 2)
            }

        actual = r.json().get("corrected", "")
        passed = actual.strip() == expected_output.strip()

        return {
            "description": description,
            "input": input_text,
            "expected": expected_output,
            "actual": actual,
            "passed": passed,
            "response_time": round((time.time() - start_time) * 1000, 2)
        }

    except Exception as e:
        return {
            "description": description,
            "input": input_text,
            "expected": expected_output,
            "actual": f"EXCEPTION: {str(e)}",
            "passed": False,
            "response_time": round((time.time() - start_time) * 1000, 2)
        }


def print_test_result(result, show_details=True):
    """Print individual test result"""
    status = "✅" if result["passed"] else "❌"
    print(f"{status} {result['description']}")

    if not result["passed"] and show_details:
        print(f"   Input:    '{result['input']}'")
        print(f"   Expected: '{result['expected']}'")
        print(f"   Actual:   '{result['actual']}'")
        if result["response_time"] > 100:
            print(f"   ⏱️  Slow: {result['response_time']}ms")


def run_test_suite(suite_name, tests, results):
    """Run a suite of tests"""
    print(f"\n📌 {suite_name}\n")
    print("-" * 50)

    for inp, exp, desc in tests:
        result = test_correction(inp, exp, desc)
        results.append(result)
        print_test_result(result)

    return results


def main():
    print("\n" + "=" * 70)
    print("🔍 COMPREHENSIVE LOWERCASE 'i' → UPPERCASE 'I' TEST")
    print("=" * 70 + "\n")

    results = []

    # ============================================
    # SUITE 1: BASIC STANDALONE "i"
    # ============================================
    basic_tests = [
        # Sentence start
        ("i am happy", "I am happy", "i at sentence start"),
        ("i think so", "I think so", "i think → I think"),
        ("i dont know", "I don't know", "i + contraction fix"),

        # Simple middle positions
        ("yesterday i went home", "Yesterday I went home", "i in middle"),
        ("when i was young", "When I was young", "when i → when I"),
        ("but i dont care", "But I don't care", "but i → but I"),
        ("so i decided", "So I decided", "so i → so I"),
        ("then i left", "Then I left", "then i → then I"),

        # With common verbs
        ("i have a car", "I have a car", "i have"),
        ("i want to go", "I want to go", "i want"),
        ("i need help", "I need help", "i need"),
        ("i like pizza", "I like pizza", "i like"),
        ("i can do it", "I can do it", "i can"),
    ]

    results = run_test_suite("Test 1: Basic Standalone 'i'", basic_tests, results)

    # ============================================
    # SUITE 2: PUNCTUATION CONTEXTS
    # ============================================
    punctuation_tests = [
        # After sentence-ending punctuation
        ("hello. i am here", "Hello. I am here", "i after period"),
        ("really? i agree", "Really? I agree", "i after question mark"),
        ("stop! i mean it", "Stop! I mean it", "i after exclamation"),

        # After commas and mid-sentence punctuation
        ("yes, i understand", "Yes, I understand", "i after comma"),
        ("well, i think so", "Well, I think so", "i after comma + well"),
        ("ok, i will go", "Ok, I will go", "i after comma + ok"),
        ("no, i dont", "No, I don't", "i after comma + no"),

        # With quotation marks
        ('he said "i know"', 'He said "I know"', 'i in quotes'),
        ("'i am here' she said", "'I am here' she said", "i in single quotes"),

        # With parentheses
        ("(i think) it's good", "(I think) it's good", "i in parentheses"),
        ("if i go (and i will)", "If I go (and I will)", "multiple i with parens"),
    ]

    results = run_test_suite("Test 2: Punctuation Contexts", punctuation_tests, results)

    # ============================================
    # SUITE 3: CONTRACTIONS
    # ============================================
    contraction_tests = [
        # Basic contractions
        ("i'm happy", "I'm happy", "i'm → I'm"),
        ("i'll be there", "I'll be there", "i'll → I'll"),
        ("i've seen it", "I've seen it", "i've → I've"),
        ("i'd like that", "I'd like that", "i'd → I'd"),

        # Contractions in sentences
        ("yesterday i'm told you", "Yesterday I'm told you", "i'm in middle"),
        ("i think i'll go", "I think I'll go", "i + i'll combo"),
        ("i know i've done it", "I know I've done it", "multiple contractions"),
        ("if i'd known", "If I'd known", "i'd in condition"),

        # Negative contractions
        ("i'm not sure", "I'm not sure", "i'm not"),
        ("i won't go", "I won't go", "i won't"),
        ("i can't believe", "I can't believe", "i can't"),
        ("i don't know", "I don't know", "i don't"),
        ("i haven't seen", "I haven't seen", "i haven't"),
    ]

    results = run_test_suite("Test 3: Contractions", contraction_tests, results)

    # ============================================
    # SUITE 4: MULTIPLE "i" IN COMPLEX SENTENCES
    # ============================================
    multiple_i_tests = [
        # Double "i" patterns
        ("i think i am right", "I think I am right", "double i simple"),
        ("i know i should go", "I know I should go", "double i know"),
        ("i wish i could", "I wish I could", "double i wish"),
        ("i feel i need", "I feel I need", "double i feel"),

        # Triple "i" patterns
        ("i think i know i can", "I think I know I can", "triple i"),
        ("i believe i saw i was", "I believe I saw I was", "triple i past"),

        # Complex sentence structures
        ("when i was young i thought i knew everything",
         "When I was young I thought I knew everything",
         "complex triple i"),

        ("i don't know what i should do or where i should go",
         "I don't know what I should do or where I should go",
         "complex multiple i"),

        ("if i go and i think i will then i know i can",
         "If I go and I think I will then I know I can",
         "complex conditional i"),
    ]

    results = run_test_suite("Test 4: Multiple 'i' in Complex Sentences", multiple_i_tests, results)

    # ============================================
    # SUITE 5: EDGE CASES & FALSE POSITIVES
    # ============================================
    edge_case_tests = [
        # Should NOT capitalize (false positives)
        ("iphone is good", "Iphone is good", "iPhone - NOT pronoun"),
        ("in it", "In it", "'in' word - NOT pronoun i"),
        ("idea is good", "Idea is good", "'idea' - NOT pronoun"),
        ("via email", "Via email", "'via' - NOT pronoun"),
        ("india country", "India country", "'India' - proper noun"),
        ("pizza with italian", "Pizza with italian", "'italian' - adjective"),

        # Tricky word boundaries
        ("i.phone", "I.phone", "i.phone - NOT pronoun"),
        ("i-pad", "I-pad", "i-pad - NOT pronoun"),
        ("i think", "I think", "i think - SHOULD capitalize"),

        # Mixed case scenarios
        ("I think i should", "I think I should", "mixed I/i correction"),
        ("i think I should", "I think I should", "mixed i/I normalization"),

        # With numbers and symbols
        ("i have 2 cars", "I have 2 cars", "i with numbers"),
        ("i #love it", "I #love it", "i with hashtag"),
        ("i @someone", "I @someone", "i with mention"),
    ]

    results = run_test_suite("Test 5: Edge Cases & False Positives", edge_case_tests, results)

    # ============================================
    # SUITE 6: REAL USER CHAT PATTERNS
    # ============================================
    chat_pattern_tests = [
        # Common chat mistakes
        ("i think your right", "I think you're right", "i + your/you're"),
        ("i dont know where he goed", "I don't know where he went", "i + grammar"),
        ("i was thinking i should go", "I was thinking I should go", "double i thinking"),
        ("yesterday i go to store", "Yesterday I went to store", "i + tense"),

        # Informal speech patterns
        ("omg i cant believe it", "Omg I can't believe it", "i + omg"),
        ("lol i know right", "Lol I know right", "i + lol"),
        ("btw i think so", "Btw I think so", "i + btw"),

        # Question patterns
        ("why i should go", "Why I should go", "why i - tricky case"),
        ("how i can help", "How I can help", "how i - tricky case"),
        ("when i can come", "When I can come", "when i - should capitalize"),

        # With slang and abbreviations
        ("imo i think its good", "Imo I think it's good", "i + imo"),
        ("tbh i dont care", "Tbh I don't care", "i + tbh"),
        ("idk i guess so", "Idk I guess so", "i + idk"),
    ]

    results = run_test_suite("Test 6: Real User Chat Patterns", chat_pattern_tests, results)

    # ============================================
    # SUITE 7: PERFORMANCE & LONG TEXTS
    # ============================================
    performance_tests = [
        # Longer paragraphs with multiple "i"
        ("i think i should tell you that i have been thinking about this for a while and i believe i know what i want to do. i hope you understand that i need to make this decision myself because i feel i am old enough to know what i am doing.",
         "I think I should tell you that I have been thinking about this for a while and I believe I know what I want to do. I hope you understand that I need to make this decision myself because I feel I am old enough to know what I am doing.",
         "long paragraph with multiple i"),

        # Mixed content with URLs and special formats
        ("i visited https://example.com yesterday and i think i found what i was looking for. i also checked my email at test@test.com and i think i got the confirmation i needed.",
         "I visited https://example.com yesterday and I think I found what I was looking for. I also checked my email at test@test.com and I think I got the confirmation I needed.",
         "mixed content with URLs and emails"),
    ]

    results = run_test_suite("Test 7: Performance & Long Texts", performance_tests, results)

    # ============================================
    # SUITE 8: CONTEXTUAL CHALLENGES
    # ============================================
    contextual_tests = [
        # With other grammar corrections
        ("i were wrong", "I was wrong", "i were → I was"),
        ("me and i was there", "I and I were there", "pronoun + i combo"),
        ("i is happy", "I am happy", "i is → I am"),
        ("i has a car", "I have a car", "i has → I have"),

        # Complex grammatical structures
        ("between you and i", "Between you and I", "between you and i"),
        ("it was i who called", "It was I who called", "it was i"),
        ("i myself think", "I myself think", "i myself"),

        # With prepositions and conjunctions
        ("for i know", "For I know", "for i"),
        ("and i think", "And I think", "and i"),
        ("or i could", "Or I could", "or i"),
        ("but i thought", "But I thought", "but i"),
    ]

    results = run_test_suite("Test 8: Contextual Challenges", contextual_tests, results)

    # ============================================
    # SUMMARY & ANALYSIS
    # ============================================
    print("\n" + "=" * 70)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    success_rate = round((passed / total) * 100, 2)

    slow_tests = [r for r in results if r["response_time"] > 100]
    failed_tests = [r for r in results if not r["passed"]]

    print(f"📊 COMPREHENSIVE RESULTS: {passed}/{total} passed ({success_rate}%)")

    # Category breakdown
    categories = {
        "Basic Standalone": results[0:15],
        "Punctuation": results[15:30],
        "Contractions": results[30:45],
        "Multiple i": results[45:55],
        "Edge Cases": results[55:70],
        "Chat Patterns": results[70:85],
        "Performance": results[85:87],
        "Contextual": results[87:]
    }

    print(f"\n📈 CATEGORY BREAKDOWN:")
    for name, tests in categories.items():
        cat_passed = sum(1 for t in tests if t["passed"])
        cat_total = len(tests)
        cat_rate = round((cat_passed / cat_total) * 100, 2) if cat_total > 0 else 0
        print(f"   {name:<15} {cat_passed:2d}/{cat_total:2d} ({cat_rate:5.1f}%)")

    # Performance analysis
    avg_time = sum(r["response_time"] for r in results) / len(results)
    print(f"\n⏱️  PERFORMANCE:")
    print(f"   Average response time: {avg_time:.1f}ms")
    print(f"   Slow tests (>100ms): {len(slow_tests)}")

    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for test in failed_tests[:5]:  # Show first 5 failures
            print(f"   - {test['description']}")
        if len(failed_tests) > 5:
            print(f"   ... and {len(failed_tests) - 5} more")

    print("\n" + "=" * 70)

    if success_rate == 100:
        print("🎉 PERFECT! ALL 'i' CAPITALIZATIONS WORKING")
    elif success_rate >= 95:
        print("✅ EXCELLENT! Almost all 'i' capitalizations working")
    elif success_rate >= 85:
        print("⚠️  GOOD! Most 'i' capitalizations work - minor fixes needed")
    else:
        print("❌ NEEDS WORK! Significant 'i' capitalization issues")

    print("=" * 70 + "\n")

    # Save detailed results
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total,
            "passed": passed,
            "success_rate": success_rate,
            "performance": {
                "average_response_time_ms": round(avg_time, 2),
                "slow_tests_count": len(slow_tests),
                "failed_tests_count": len(failed_tests)
            }
        },
        "category_breakdown": {
            name: {
                "passed": sum(1 for t in tests if t["passed"]),
                "total": len(tests),
                "success_rate": round((sum(1 for t in tests if t["passed"]) / len(tests)) * 100, 2) if len(tests) > 0 else 0
            }
            for name, tests in categories.items()
        },
        "failed_tests": [
            {
                "description": t["description"],
                "input": t["input"],
                "expected": t["expected"],
                "actual": t["actual"],
                "response_time": t["response_time"]
            }
            for t in failed_tests
        ],
        "slow_tests": [
            {
                "description": t["description"],
                "response_time": t["response_time"]
            }
            for t in slow_tests if t["response_time"] > 200
        ],
        "all_results": results
    }

    with open("I_CAPITALIZATION_TEST.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("💾 Detailed results saved to: I_CAPITALIZATION_TEST.json")
    print("📋 Failed tests details saved for debugging\n")


def health_check():
    """Verify server is running"""
    try:
        r = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('status') == 'healthy' and data.get('correctors'):
                print("✅ Server is healthy and correctors are loaded")
                return True
        print("❌ Server not healthy")
        return False
    except:
        print("❌ Server not running at http://127.0.0.1:5000")
        print("   Start it with: python app.py")
        return False


if __name__ == "__main__":
    if not health_check():
        exit(1)

    print("🚀 Starting comprehensive 'i' capitalization test suite...")
    print("   This will test 100+ different scenarios")
    print("   Please wait...\n")

    main()