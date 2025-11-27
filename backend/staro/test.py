import requests
import json
import time

BASE_URL = "http://localhost:5000"


def print_separator():
    print("\n" + "=" * 60)


def test_health():
    print_separator()
    print("🏥 TESTING HEALTH ENDPOINT")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")


def test_home():
    print_separator()
    print("🏠 TESTING HOME ENDPOINT")
    try:
        response = requests.get(BASE_URL)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Message: {data.get('message')}")
    except Exception as e:
        print(f"❌ Home endpoint failed: {e}")


def test_correction():
    print_separator()
    print("📝 TESTING TEXT CORRECTION")

    test_cases = [
        "I hav a dreem to writte a bookk one day",
        "This is an exemple of bad english",
        "She go to the store yestaday",
        "The weather is beutiful today",
        "They was very happy to see us"
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"📥 Original: {text}")

        try:
            response = requests.post(
                f"{BASE_URL}/correct",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Corrected: {result['corrected_text']}")
                print(f"🔄 Changes: {result['changes_made']}")
                print(f"📊 Words: {result['word_count']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            print("⏰ Request timeout")
        except Exception as e:
            print(f"🚨 Request failed: {e}")

        # Mali delay između zahteva
        time.sleep(0.5)


def test_error_cases():
    print_separator()
    print("🚨 TESTING ERROR CASES")

    # Test praznog teksta
    print("\n1. Testing empty text:")
    response = requests.post(f"{BASE_URL}/correct", json={"text": ""})
    print(f"Status: {response.status_code}, Response: {response.json()}")

    # Test bez text polja
    print("\n2. Testing missing text field:")
    response = requests.post(f"{BASE_URL}/correct", json={"something": "else"})
    print(f"Status: {response.status_code}, Response: {response.json()}")


if __name__ == "__main__":
    print("🚀 STARTING AI TEXT CORRECTOR API TESTS")
    print("📍 Base URL:", BASE_URL)

    test_health()
    test_home()
    test_correction()
    test_error_cases()

    print_separator()
    print("🎉 ALL TESTS COMPLETED!")