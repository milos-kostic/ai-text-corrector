"""
production_benchmark.py
========================
Quick benchmark to answer: "Can I launch this and make money?"

Tests ONLY what matters:
1. Is it fast enough? (< 500ms average)
2. Can it handle 10 concurrent users? (basic load)
3. Does batch work? (for commercial customers)
4. Any crashes? (stability)

Run time: ~30 seconds
"""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

API_URL = "http://127.0.0.1:5000"

# Test texts (realistic user inputs)
TESTS = [
    "i dont think this is corect",
    "she dont know where he goed",
    "this are bad sentence",
    "your going to love this",
    "their happy about the news",
]


def test_single_request(text):
    """Single request - measure time"""
    start = time.time()
    try:
        r = requests.post(f"{API_URL}/correct", json={"text": text}, timeout=10)
        ms = (time.time() - start) * 1000
        return {
            "success": r.status_code == 200,
            "time_ms": ms,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "time_ms": 0,
            "error": str(e)
        }


def test_batch_request(texts):
    """Batch request"""
    start = time.time()
    try:
        r = requests.post(f"{API_URL}/correct/batch", json={"texts": texts}, timeout=30)
        ms = (time.time() - start) * 1000
        return {
            "success": r.status_code == 200,
            "time_ms": ms,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "time_ms": 0,
            "error": str(e)
        }


def run_benchmark():
    print("\n" + "=" * 60)
    print("⚡ PRODUCTION READINESS BENCHMARK")
    print("=" * 60 + "\n")

    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "verdict": ""
    }

    # ============================================
    # TEST 1: Response Time (Critical)
    # ============================================
    print("1️⃣  Response Time Test (20 requests)...")

    times = []
    failures = 0

    for i in range(20):
        text = TESTS[i % len(TESTS)]
        result = test_single_request(text)

        if result["success"]:
            times.append(result["time_ms"])
        else:
            failures += 1
            print(f"   ✗ Request {i + 1} failed: {result['error']}")

    if times:
        avg_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]

        results["tests"]["response_time"] = {
            "avg_ms": round(avg_time, 2),
            "p95_ms": round(p95_time, 2),
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2),
            "failures": failures,
            "passed": avg_time < 500 and failures == 0
        }

        print(f"   ✓ Average: {avg_time:.0f}ms")
        print(f"   ✓ 95th percentile: {p95_time:.0f}ms")
        print(f"   ✓ Range: {min(times):.0f}ms - {max(times):.0f}ms")

        if avg_time < 500:
            print(f"   ✅ PASS - Fast enough for production")
        else:
            print(f"   ⚠️  WARNING - Slower than ideal (>500ms avg)")
    else:
        results["tests"]["response_time"] = {"passed": False, "error": "All requests failed"}
        print("   ❌ FAIL - All requests failed")

    # ============================================
    # TEST 2: Concurrent Users (Critical)
    # ============================================
    print("\n2️⃣  Concurrency Test (10 simultaneous users)...")

    def concurrent_request(i):
        text = TESTS[i % len(TESTS)]
        return test_single_request(text)

    start = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        concurrent_results = list(executor.map(concurrent_request, range(10)))
    total_time = (time.time() - start) * 1000

    concurrent_times = [r["time_ms"] for r in concurrent_results if r["success"]]
    concurrent_failures = sum(1 for r in concurrent_results if not r["success"])

    if concurrent_times:
        results["tests"]["concurrency"] = {
            "total_time_ms": round(total_time, 2),
            "avg_request_ms": round(statistics.mean(concurrent_times), 2),
            "failures": concurrent_failures,
            "passed": concurrent_failures == 0
        }

        print(f"   ✓ Completed in: {total_time:.0f}ms")
        print(f"   ✓ Avg per request: {statistics.mean(concurrent_times):.0f}ms")
        print(f"   ✓ Failures: {concurrent_failures}")

        if concurrent_failures == 0:
            print(f"   ✅ PASS - Can handle concurrent users")
        else:
            print(f"   ❌ FAIL - {concurrent_failures} requests failed under load")
    else:
        results["tests"]["concurrency"] = {"passed": False, "error": "All concurrent requests failed"}
        print("   ❌ FAIL - Cannot handle concurrent load")

    # ============================================
    # TEST 3: Batch Processing (Commercial)
    # ============================================
    print("\n3️⃣  Batch Processing Test (50 texts)...")

    batch_texts = TESTS * 10  # 50 texts
    batch_result = test_batch_request(batch_texts)

    if batch_result["success"]:
        per_text = batch_result["time_ms"] / len(batch_texts)

        results["tests"]["batch"] = {
            "batch_size": len(batch_texts),
            "total_time_ms": round(batch_result["time_ms"], 2),
            "time_per_text_ms": round(per_text, 2),
            "passed": True
        }

        print(f"   ✓ Batch of {len(batch_texts)} texts: {batch_result['time_ms']:.0f}ms")
        print(f"   ✓ Per text: {per_text:.0f}ms")
        print(f"   ✅ PASS - Batch processing works")
    else:
        results["tests"]["batch"] = {"passed": False, "error": batch_result["error"]}
        print(f"   ❌ FAIL - Batch processing failed: {batch_result['error']}")

    # ============================================
    # TEST 4: Error Handling (Stability)
    # ============================================
    print("\n4️⃣  Error Handling Test...")

    error_tests = [
        ("Empty text", {"text": ""}),
        ("Missing field", {"wrong": "field"}),
        ("Long text", {"text": "x" * 60000}),
    ]

    error_handling_ok = True
    for name, payload in error_tests:
        try:
            r = requests.post(f"{API_URL}/correct", json=payload, timeout=10)
            # We expect 4xx errors, not crashes
            if r.status_code >= 500:
                print(f"   ✗ {name}: Server crashed (500)")
                error_handling_ok = False
            else:
                print(f"   ✓ {name}: Handled correctly ({r.status_code})")
        except Exception as e:
            print(f"   ✗ {name}: Connection failed")
            error_handling_ok = False

    results["tests"]["error_handling"] = {"passed": error_handling_ok}

    if error_handling_ok:
        print(f"   ✅ PASS - Errors handled gracefully")
    else:
        print(f"   ❌ FAIL - Server crashes on bad input")

    # ============================================
    # FINAL VERDICT
    # ============================================
    print("\n" + "=" * 60)

    all_passed = all(
        test.get("passed", False)
        for test in results["tests"].values()
    )

    if all_passed:
        verdict = "✅ READY FOR PRODUCTION"
        verdict_detail = "All critical tests passed. You can launch."
        results["verdict"] = "PASS"
    else:
        failed_tests = [
            name for name, test in results["tests"].items()
            if not test.get("passed", False)
        ]
        verdict = "⚠️  NEEDS ATTENTION"
        verdict_detail = f"Failed: {', '.join(failed_tests)}"
        results["verdict"] = "FAIL"

    print(f"VERDICT: {verdict}")
    print(f"Details: {verdict_detail}")
    print("=" * 60 + "\n")

    # Save detailed results
    import json
    with open("PRODUCTION_BENCHMARK.json", "w") as f:
        json.dump(results, f, indent=2)

    print("📊 Full results saved to: PRODUCTION_BENCHMARK.json\n")

    return results


if __name__ == "__main__":
    try:
        # Quick health check first
        r = requests.get(f"{API_URL}/health", timeout=5)
        if r.status_code != 200:
            print("❌ Server not healthy. Check /health endpoint.")
            exit(1)
    except:
        print("❌ Server not running at", API_URL)
        print("Start it with: python app.py")
        exit(1)

    run_benchmark()