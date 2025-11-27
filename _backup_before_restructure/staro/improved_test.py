import requests
import time
import json
from typing import Dict, List, Tuple, Any


class GrammarTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        self.category_results = {}

    def run_test(self, test_name: str, input_text: str, expected: str, category: str = "General") -> Dict[str, Any]:
        """Run a single test and return results"""
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/correct",
                json={"text": input_text},
                timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                result = response.json()
                actual = result['corrected']
                changed = result['changed']

                # Determine if test passed
                if expected.lower() == "empty text error":
                    passed = False
                    notes = f"Expected error but got success"
                else:
                    passed = (actual == expected)
                    notes = f"Response time: {response_time:.2f}ms, Changes: {changed}"

            elif response.status_code == 400:
                result = response.json()
                actual = f"HTTP 400: {json.dumps(result)}"

                if expected.lower() == "empty text error":
                    passed = True
                    notes = "Correctly returned empty text error"
                else:
                    passed = False
                    notes = f"Unexpected error: {actual}"

            else:
                actual = f"HTTP {response.status_code}"
                passed = False
                notes = f"Unexpected status code: {response.status_code}"

        except requests.exceptions.Timeout:
            response_time = (time.time() - start_time) * 1000
            actual = "Timeout"
            passed = False
            notes = f"Request timed out after {response_time:.2f}ms"

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            actual = f"Error: {str(e)}"
            passed = False
            notes = f"Exception: {str(e)}"

        test_result = {
            'test_name': test_name,
            'category': category,
            'input': input_text,
            'expected': expected,
            'actual': actual,
            'passed': passed,
            'notes': notes,
            'response_time': response_time
        }

        self.results.append(test_result)

        # Update category results
        if category not in self.category_results:
            self.category_results[category] = {'total': 0, 'passed': 0}

        self.category_results[category]['total'] += 1
        if passed:
            self.category_results[category]['passed'] += 1

        return test_result

    def run_pronoun_test(self, test_name: str, input_text: str, expected: str) -> Dict[str, Any]:
        """Special test for pronoun preservation with detailed checking"""
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/correct",
                json={"text": input_text},
                timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                result = response.json()
                actual = result['corrected']

                # Check if pronouns are preserved
                pronouns_preserved = True
                input_words = input_text.split()
                actual_words = actual.split()

                # Simple check: compare word by word for pronouns
                for i, (input_word, actual_word) in enumerate(zip(input_words, actual_words)):
                    lower_input = input_word.lower()
                    if lower_input in ['i', 'you', 'he', 'she', 'we', 'they', 'it', 'me', 'him', 'her', 'us', 'them']:
                        if input_word != actual_word:
                            pronouns_preserved = False
                            break

                passed = (actual == expected) and pronouns_preserved
                notes = f"Pronouns preserved: {pronouns_preserved}, Response: {response_time:.2f}ms"

            else:
                actual = f"HTTP {response.status_code}"
                passed = False
                notes = f"Unexpected status code: {response.status_code}"

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            actual = f"Error: {str(e)}"
            passed = False
            notes = f"Exception: {str(e)}"

        test_result = {
            'test_name': test_name,
            'category': 'Pronoun Preservation',
            'input': input_text,
            'expected': expected,
            'actual': actual,
            'passed': passed,
            'notes': notes,
            'response_time': response_time
        }

        self.results.append(test_result)
        self._update_category_results('Pronoun Preservation', passed)
        return test_result

    def run_complex_test(self, test_name: str, input_text: str, expected: str) -> Dict[str, Any]:
        """Test for complex sentences with similarity scoring"""
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/correct",
                json={"text": input_text},
                timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                result = response.json()
                actual = result['corrected']

                # Calculate similarity
                similarity = self._calculate_similarity(expected, actual)

                # Pass if similarity is high enough (adjust threshold as needed)
                passed = similarity >= 80.0
                notes = f"Similarity: {similarity:.1f}%, Response: {response_time:.2f}ms"

            else:
                actual = f"HTTP {response.status_code}"
                passed = False
                notes = f"Unexpected status code: {response.status_code}"

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            actual = f"Error: {str(e)}"
            passed = False
            notes = f"Exception: {str(e)}"

        test_result = {
            'test_name': test_name,
            'category': 'Complex Sentences',
            'input': input_text,
            'expected': expected,
            'actual': actual,
            'passed': passed,
            'notes': notes,
            'response_time': response_time
        }

        self.results.append(test_result)
        self._update_category_results('Complex Sentences', passed)
        return test_result

    def run_performance_test(self, test_name: str, input_text: str, expected: str = "Success") -> Dict[str, Any]:
        """Performance-focused tests"""
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/correct",
                json={"text": input_text},
                timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                result = response.json()
                actual = f"Success in {response_time:.2f}ms"
                passed = True
                notes = f"Response: {response_time:.2f}ms, Length: {len(input_text)} chars"
            else:
                actual = f"HTTP {response.status_code}"
                passed = False
                notes = f"Failed with status: {response.status_code}"

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            actual = f"Error: {str(e)}"
            passed = False
            notes = f"Exception: {str(e)}"

        test_result = {
            'test_name': test_name,
            'category': 'Performance',
            'input': input_text,
            'expected': expected,
            'actual': actual,
            'passed': passed,
            'notes': notes,
            'response_time': response_time
        }

        self.results.append(test_result)
        self._update_category_results('Performance', passed)
        return test_result

    def _update_category_results(self, category: str, passed: bool):
        """Update category results"""
        if category not in self.category_results:
            self.category_results[category] = {'total': 0, 'passed': 0}

        self.category_results[category]['total'] += 1
        if passed:
            self.category_results[category]['passed'] += 1

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple similarity between two strings"""
        if not str1 and not str2:
            return 100.0
        if not str1 or not str2:
            return 0.0

        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())

        if not words1 and not words2:
            return 100.0

        common_words = words1.intersection(words2)
        all_words = words1.union(words2)

        return (len(common_words) / len(all_words)) * 100

    def print_results(self):
        """Print comprehensive test results"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['passed'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print("=" * 100)
        print("🚀 COMPREHENSIVE GRAMMAR CORRECTOR TEST REPORT")
        print("=" * 100)
        print(f"Test Date: {time.strftime('%Y-%m-%dT%H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        print("CATEGORY SUMMARY:")
        print("-" * 50)
        for category, stats in self.category_results.items():
            percentage = (stats['passed'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"{category:20} {stats['passed']:2d}/{stats['total']:2d} ({percentage:5.1f}%)")

        print("\n" + "=" * 100)
        print("DETAILED TEST RESULTS:")
        print("=" * 100)

        current_category = ""
        for result in self.results:
            if result['category'] != current_category:
                current_category = result['category']
                print(f"\n{current_category}:")
                print("-" * 80)

            emoji = "🟢" if result['passed'] else "🔴"
            print(f"{emoji} {result['test_name']}")
            print(f"   Input:    {result['input']}")
            print(f"   Expected: {result['expected']}")
            print(f"   Actual:   {result['actual']}")
            print(f"   Notes:    {result['notes']}")
            print()

    def get_performance_stats(self) -> Dict[str, float]:
        """Calculate performance statistics"""
        response_times = [r['response_time'] for r in self.results if 'response_time' in r and r['response_time'] > 0]

        if not response_times:
            return {'avg': 0, 'min': 0, 'max': 0}

        return {
            'avg': sum(response_times) / len(response_times),
            'min': min(response_times),
            'max': max(response_times)
        }


def run_comprehensive_tests(base_url: str = "http://localhost:5000"):
    """Run all comprehensive tests"""
    tester = GrammarTester(base_url)

    # Basic Spelling Tests
    print("Running Basic Spelling tests...")
    spelling_tests = [
        ("Basic 'the' misspelling", "teh", "the"),
        ("Basic 'and' misspelling", "adn", "and"),
        ("Their/they're/there confusion", "thier", "their"),
        ("I before E rule", "recieve", "receive"),
        ("Common definite misspelling", "definately", "definitely"),
        ("Common separate misspelling", "seperate", "separate"),
        ("Double C misspelling", "accross", "across"),
        ("Double L misspelling", "untill", "until"),
        ("Double C and R", "occured", "occurred"),
        ("Single M rule", "comming", "coming"),
        ("N after R", "goverment", "government"),
        ("Remove E", "truely", "truly"),
        ("Double L", "realy", "really"),
        ("A instead of E", "exemple", "example"),
        ("Common beauty misspelling", "beautiful", "beautiful"),
        ("Single T", "writting", "writing"),
        ("Double N", "begining", "beginning"),
        ("N instead of M", "environement", "environment"),
        ("Single C, double S", "neccessary", "necessary"),
        ("No O after N", "pronounciation", "pronunciation"),
        ("Internet slang", "u", "you"),
        ("Internet slang", "ur", "your"),
        ("Internet slang", "thx", "thanks"),
        ("Internet slang", "plz", "please"),
        ("Internet slang", "sry", "sorry"),
        ("Internet slang", "ppl", "people"),
        ("Internet slang", "b4", "before"),
        ("Internet slang", "2day", "today"),
        ("Internet slang", "gr8", "great"),
        ("Internet slang", "l8r", "later"),
    ]

    for test_name, input_text, expected in spelling_tests:
        tester.run_test(test_name, input_text, expected, "Basic Spelling")

    # Grammar Rules Tests
    print("Running Grammar Rules tests...")
    grammar_tests = [
        ("3rd person singular - have/has", "he have", "he has"),
        ("3rd person singular - have/has", "she have", "she has"),
        ("3rd person singular - have/has", "it have", "it has"),
        ("Plural subject with has", "they has", "they have"),
        ("Plural subject with has", "we has", "we have"),
        ("2nd person with has", "you has", "you have"),
        ("3rd person singular - do/does", "he do", "he does"),
        ("3rd person singular - do/does", "she do", "she does"),
        ("3rd person singular - do/does", "it do", "it does"),
        ("Plural with does", "they does", "they do"),
        ("3rd person singular - are/is", "he are", "he is"),
        ("3rd person singular - are/is", "she are", "she is"),
        ("3rd person singular - are/is", "it are", "it is"),
        ("Plural with is", "they is", "they are"),
        ("Plural with is", "we is", "we are"),
        ("2nd person with is", "you is", "you are"),
        ("1st person past - was/were", "I were", "I was"),
        ("3rd person past - was/were", "he were", "he was"),
        ("3rd person past - was/were", "she were", "she was"),
        ("3rd person past - was/were", "it were", "it was"),
        ("Plural past - was/were", "we was", "we were"),
        ("Plural past - was/were", "they was", "they were"),
        ("2nd person past - was/were", "you was", "you were"),
        ("Past tense of go", "I goed", "I went"),
        ("Past tense of run", "he runned", "he ran"),
        ("Past tense of eat", "she eated", "she ate"),
        ("Past tense of drink", "they drinked", "they drank"),
        ("Past tense of buy", "we buyed", "we bought"),
        ("Past tense of think", "you thinked", "you thought"),
        ("Present perfect eat", "I have ate", "I have eaten"),
        ("Present perfect go", "he have went", "he has gone"),
        ("Present perfect run", "she have ran", "she has run"),
        ("Article before vowel", "a apple", "an apple"),
        ("Article before silent H", "a hour", "an hour"),
        ("Article before consonant sound", "a university", "a university"),
        ("Article before consonant", "an book", "a book"),
        ("Article before H sound", "an house", "a house"),
        ("Article before Y sound", "an European", "a European"),
    ]

    for test_name, input_text, expected in grammar_tests:
        tester.run_test(test_name, input_text, expected, "Grammar Rules")

    # Pronoun Preservation Tests
    print("Running Pronoun Preservation tests...")
    pronoun_tests = [
        ("Single pronoun I", "I", "I"),
        ("Single pronoun you", "you", "you"),
        ("Single pronoun he", "he", "he"),
        ("Single pronoun she", "she", "she"),
        ("Single pronoun we", "we", "we"),
        ("Single pronoun they", "they", "they"),
        ("Single pronoun it", "it", "it"),
        ("Pronoun I capitalization", "i am", "I am"),
        ("She with verb correction", "she dont", "she doesn't"),
        ("He with verb correction", "he have", "he has"),
        ("We with verb correction", "we was", "we were"),
        ("They with verb correction", "they has", "they have"),
        ("You with verb correction", "you is", "you are"),
        ("Multiple pronouns", "I and you", "I and you"),
        ("Multiple pronouns", "he and she", "he and she"),
        ("Multiple pronouns", "we and they", "we and they"),
        ("Object pronouns", "me and him", "me and him"),
        ("Object pronouns", "her and us", "her and us"),
    ]

    for test_name, input_text, expected in pronoun_tests:
        tester.run_pronoun_test(test_name, input_text, expected)

    # Complex Sentences Tests
    print("Running Complex Sentences tests...")
    complex_tests = [
        ("Multiple corrections in one sentence",
         "Me and my friend was going to store",
         "My friend and I were going to the store"),

        ("Multiple subject-verb agreements",
         "She dont like apples but he dont like oranges",
         "She doesn't like apples but he doesn't like oranges"),

        ("Multiple verb tense corrections",
         "Yesterday I goed to market and buyed some fruits",
         "Yesterday I went to the market and bought some fruits"),

        ("Quantifier with singular verb",
         "Each of the students have theyre own computer",
         "Each of the students has their own computer"),

        ("Collective noun with singular verb",
         "The team are playing good today",
         "The team is playing well today"),

        ("Neither with singular verb",
         "Neither of them are coming to party",
         "Neither of them is coming to the party"),

        ("One of with singular verb",
         "One of my friends are doctor",
         "One of my friends is a doctor"),

        ("There is/are agreement",
         "There is many reasons for this",
         "There are many reasons for this"),

        ("Here is/are agreement",
         "Here is the books you wanted",
         "Here are the books you wanted"),

        ("Data plural and verb agreement",
         "The data shows that people prefers simplicity",
         "The data show that people prefer simplicity"),
    ]

    for test_name, input_text, expected in complex_tests:
        tester.run_complex_test(test_name, input_text, expected)

    # Edge Cases Tests
    print("Running Edge Cases tests...")
    edge_tests = [
        ("Empty string", "", "Empty text error"),
        ("Whitespace only", "   ", "Empty text error"),
        ("Single character", "a", "a"),
        ("Single pronoun", "I", "I"),
        ("Numbers only", "123", "123"),
        ("Alphanumeric", "Hello123", "Hello123"),
        ("All uppercase", "HELLO WORLD", "HELLO WORLD"),
        ("Capitalization check", "hello world", "Hello world"),
        ("Comma spacing", "hello,world", "Hello, world"),
        ("Period spacing", "hello.world", "Hello. world"),
        ("Exclamation spacing", "hello!world", "Hello! world"),
        ("Email preservation", "test@example.com", "test@example.com"),
        ("Price format", "$19.99", "$19.99"),
        ("URL preservation", "https://example.com", "https://example.com"),
        ("Multiple space cleanup", "Multiple     spaces", "Multiple spaces"),
    ]

    for test_name, input_text, expected in edge_tests:
        tester.run_test(test_name, input_text, expected, "Edge Cases")

    # Performance Tests
    print("Running Performance tests...")
    performance_tests = [
        ("Short text with few errors", "I hav a book...", "Success"),
        ("Medium text", "The students are studing for there exams and they is working hard", "Success"),
        ("Long text with multiple errors",
         "In teh begining, there was many problms with the systm. The ppl who designed it didnt think about all the use cases. We has to fix many bugs and improve the performnce. It was a long process but finally we has a stable version that works for most users.",
         "Success"),
    ]

    for test_name, input_text, expected in performance_tests:
        tester.run_performance_test(test_name, input_text, expected)

    # Add performance timing test
    perf_stats = tester.get_performance_stats()
    perf_test = {
        'test_name': "Average Response Time",
        'category': 'Performance',
        'input': "N/A",
        'expected': "< 500ms",
        'actual': f"{perf_stats['avg']:.1f}ms",
        'passed': perf_stats['avg'] < 500,
        'notes': f"Min: {perf_stats['min']:.1f}ms, Max: {perf_stats['max']:.1f}ms",
        'response_time': perf_stats['avg']
    }
    tester.results.append(perf_test)
    tester._update_category_results('Performance', perf_test['passed'])

    # Print results
    tester.print_results()

    return tester


if __name__ == "__main__":
    import sys

    base_url = "http://localhost:5000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"Starting comprehensive grammar tests against: {base_url}")
    run_comprehensive_tests(base_url)