"""
performance_benchmark.py
========================
Performance benchmark for optimized corrector.
"""

import requests
import time
import statistics
from datetime import datetime

API_URL = "http://127.0.0.1:5000/correct"

# Test cases that showed performance spikes
PERFORMANCE_TESTS = [
    "but i dont care",  # Previously 76ms
    "i dont know where he goed",  # Previously 34ms
    "this are bad sentence",
    "your going to love this",
    "their happy about the news",
    "i think i should tell you that i have been thinking about this for a while",
    "yesterday i go to store and i think i found what i was looking for",
]

def benchmark_performance():
    print("\n=== PERFORMANCE BENCHMARK ===\n")

    results = []

    for test_text in PERFORMANCE_TESTS:
        times = []
        for _ in range(5):  # Run 5 times to get average
            start_time = time.time()
            try:
                r = requests.post(API_URL, json={"text": test_text}, timeout=10)
                if r.status_code == 200:
                    response_time = (time.time() - start_time) * 1000
                    times.append(response_time)
            except Exception as e:
                print(f"Error: {e}")
                times.append(0)

        if times:
            avg_time = statistics.mean(times)
            max_time = max(times)
            min_time = min(times)

            results.append({
                "text": test_text[:50] + "..." if len(test_text) > 50 else test_text,
                "avg_ms": round(avg_time, 2),
                "min_ms": round(min_time, 2),
                "max_ms": round(max_time, 2),
                "length": len(test_text)
            })

            status = "✅" if avg_time < 20 else "⚠️" if avg_time < 50 else "❌"
            print(f"{status} '{test_text[:30]}...'")
            print(f"   Avg: {avg_time:.1f}ms, Min: {min_time:.1f}ms, Max: {max_time:.1f}ms")

    # Summary
    print(f"\n=== SUMMARY ===")
    avg_all = statistics.mean([r["avg_ms"] for r in results])
    max_all = max([r["max_ms"] for r in results])

    print(f"Overall Average: {avg_all:.1f}ms")
    print(f"Worst Case: {max_all:.1f}ms")
    print(f"Tested {len(results)} problematic texts")

    if avg_all < 15:
        print("🎉 EXCELLENT PERFORMANCE!")
    elif avg_all < 25:
        print("✅ GOOD PERFORMANCE")
    else:
        print("⚠️  NEEDS OPTIMIZATION")

if __name__ == "__main__":
    benchmark_performance()