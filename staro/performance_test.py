import requests
import time
import json
from datetime import datetime


class PerformanceTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []

    def generate_long_text(self, length_chars):
        """Generiše dugi tekst sa različitim sadržajem"""
        base_text = """
        Ovo je primer dužeg teksta koji testira performance text corrector servisa.
        Tekst sadrži različite elemente: email adrese kao test@example.com, 
        URL-ove kao https://google.com, telefone +381 11 123 4567, 
        i cene kao $199.99 ili €49.99. Ovo je veoma važno za testiranje 
        performansi sistema pri realnom opterećenju.

        Servis mora da podrži različite formate teksta uključujući specijalne 
        karaktere, interpunkciju i različite jezičke konstrukcije. 
        Performance testing je ključan za proveru skalabilnosti aplikacije.

        """

        # Ponavljaj base_text dok ne dostigne željenu dužinu
        repeated_text = (base_text * (length_chars // len(base_text) + 1))[:length_chars]
        return repeated_text.strip()

    def test_long_text(self, name, length_chars):
        """Testira performance za tekst određene dužine"""
        print(f"Testiram: {name} ({length_chars} karaktera)...")

        text = self.generate_long_text(length_chars)
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/correct",
                json={"text": text},
                timeout=30  # Povećaj timeout za duže tekstove
            )

            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                success = True
                corrected_length = len(data.get("corrected", ""))
                changed = data.get("changed", False)
            else:
                success = False
                corrected_length = 0
                changed = False

            result = {
                "test_name": name,
                "text_length": length_chars,
                "response_time_ms": round(response_time, 2),
                "success": success,
                "status_code": response.status_code,
                "corrected_length": corrected_length,
                "changed": changed,
                "timestamp": datetime.now().isoformat()
            }

        except requests.exceptions.Timeout:
            result = {
                "test_name": name,
                "text_length": length_chars,
                "response_time_ms": -1,
                "success": False,
                "status_code": "TIMEOUT",
                "corrected_length": 0,
                "changed": False,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            result = {
                "test_name": name,
                "text_length": length_chars,
                "response_time_ms": -1,
                "success": False,
                "status_code": f"ERROR: {str(e)}",
                "corrected_length": 0,
                "changed": False,
                "timestamp": datetime.now().isoformat()
            }

        self.results.append(result)
        print(f"  → Vreme: {result['response_time_ms']}ms, Uspeh: {result['success']}")
        return result

    def test_memory_usage(self, num_requests=100):
        """Testira memory usage sa više uzastopnih zahteva"""
        print(f"\nMemory test: {num_requests} uzastopnih zahteva...")

        test_text = self.generate_long_text(1000)  # 1k karaktera po zahtevu
        times = []

        for i in range(num_requests):
            start_time = time.time()

            try:
                response = requests.post(
                    f"{self.base_url}/correct",
                    json={"text": f"{test_text} - request {i}"},
                    timeout=10
                )
                response_time = (time.time() - start_time) * 1000
                times.append(response_time)

                if i % 20 == 0:  # Log na svakih 20 zahteva
                    print(f"  Zahtev {i}: {response_time:.2f}ms")

            except Exception as e:
                print(f"  ❌ Zahtev {i} fail: {e}")
                times.append(-1)

        # Analiza performansi
        successful_times = [t for t in times if t > 0]
        if successful_times:
            avg_time = sum(successful_times) / len(successful_times)
            max_time = max(successful_times)
            min_time = min(successful_times)

            result = {
                "test_type": "memory_usage",
                "total_requests": num_requests,
                "successful_requests": len(successful_times),
                "avg_response_time_ms": round(avg_time, 2),
                "max_response_time_ms": round(max_time, 2),
                "min_response_time_ms": round(min_time, 2),
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "test_type": "memory_usage",
                "total_requests": num_requests,
                "successful_requests": 0,
                "error": "All requests failed"
            }

        self.results.append(result)
        return result

    def save_results(self, filename="performance_results.json"):
        """Čuva rezultate u JSON formatu"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n📊 Rezultati sačuvani u: {filename}")

        # Prikaz summary
        successful_tests = [r for r in self.results if r.get('success')]
        print(f"Ukupno testova: {len(self.results)}")
        print(f"Uspešnih testova: {len(successful_tests)}")

        if successful_tests:
            avg_time = sum(r['response_time_ms'] for r in successful_tests if
                           'response_time_ms' in r and r['response_time_ms'] > 0) / len(successful_tests)
            print(f"Prosečno vreme odgovora: {avg_time:.2f}ms")


def run_performance_tests():
    """Pokreće sve performance testove"""
    tester = PerformanceTester()

    print("🚀 POKRETANJE PERFORMANCE TESTOVA")
    print("=" * 50)

    # Testovi različitih dužina teksta
    text_lengths = [
        ("Kratak tekst", 500),
        ("Srednji tekst", 5000),
        ("Dug tekst", 10000),
        ("Veoma dug tekst", 25000),
        ("Ekstremno dug tekst", 50000),
    ]

    for name, length in text_lengths:
        tester.test_long_text(name, length)

    # Memory usage test
    tester.test_memory_usage(num_requests=50)  # Počni sa 50 zahteva

    # Sačuvaj rezultate
    tester.save_results()

    print("\n🎯 PERFORMANCE TEST ZAVRŠEN")
    print("Proverite 'performance_results.json' za detaljne rezultate")


if __name__ == "__main__":
    run_performance_tests()