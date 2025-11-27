import requests
import json


def manual_test():
    url = "http://localhost:5000/correct"

    # Test cases sa različitim greškama
    test_texts = [
        "Helo world, how are you todai?",
        "I cant beleive its already Wensday",
        "The students are studing for there exams",
        "She dont like coffee, but he do",
        "We was going to the park when it started to rain"
    ]

    for text in test_texts:
        print(f"\n🔹 Testing: '{text}'")

        response = requests.post(url, json={"text": text})

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Corrected: '{result['corrected_text']}'")
            print(f"📈 Changes made: {result['changes_made']}")
            print(f"📊 Stats: {result['word_count']} words, {result['character_count']} chars")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    print("🎯 MANUAL TESTING - REAL WORLD EXAMPLES")
    manual_test()