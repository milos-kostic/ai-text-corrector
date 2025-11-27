# run_all_tests - organized version with CSV and TXT output in code_and_tests_collected folder
import subprocess
import sys
import os
import csv
from datetime import datetime


def run_all_tests():
    """Run all test files sequentially"""
    print("RUNNING ALL TESTS")
    print("=" * 50)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    possible_paths = ['.', 'tests', './tests']

    test_files = [
        'test_basic.py',
        'test_spelling.py',
        'test_grammar.py',
        'test_edge_cases.py'
    ]

    found_files = []

    # Locate test files
    for test_file in test_files:
        found = False
        for path in possible_paths:
            full_path = os.path.join(path, test_file)
            if os.path.exists(full_path):
                found_files.append(full_path)
                print(f"FOUND: {test_file} at: {full_path}")
                found = True
                break

        if not found:
            print(f"NOT FOUND: {test_file}")

    if not found_files:
        print("No test files found!")
        return

    total_files = len(found_files)
    successful_files = 0

    # Execute each test
    for i, test_file in enumerate(found_files, 1):
        print(f"[{i}/{total_files}] Running {test_file}...")
        print("-" * 40)

        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env,
                timeout=600
            )

            if result.returncode == 0:
                print(f"SUCCESS: {test_file} completed")
                successful_files += 1
            else:
                print(f"FAILED: {test_file} return code {result.returncode}")
                if result.stderr:
                    error_lines = result.stderr.strip().split('\n')
                    print("Error details:")
                    for line in error_lines[:3]:
                        print(f"  {line}")

            # Output summary (basic filtering)
            if result.stdout:
                output_lines = result.stdout.strip().split('\n')

                important_lines = []
                for line in output_lines:
                    low = line.lower()
                    if any(k in low for k in
                           ['success', 'rate', 'passed', 'failed', 'total', 'score']):
                        important_lines.append(line)

                if important_lines:
                    print("Output summary:")
                    for line in important_lines:
                        print(f"  {line}")

        except subprocess.TimeoutExpired:
            print(f"TIMEOUT: {test_file}")
        except Exception as e:
            print(f"ERROR: {test_file} - {str(e)}")

        print()

    print("=" * 50)
    print("ALL TESTS COMPLETED")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Successful: {successful_files}/{total_files} files")

    return True


def extract_value(content, keyword, suffix=None):
    """Ekstraktuje numeričku vrednost iz sadržaja nakon keyworda"""
    import re

    # Traži pattern: keyword broj
    pattern = rf"{keyword}\s*(\d+\.?\d*)"
    match = re.search(pattern, content, re.IGNORECASE)

    if match:
        value = match.group(1)
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except:
            return None

    return None


def display_final_results_summary():
    """Prikazuje finalne rezultate tabelarno sa sortiranjem po željenom redosledu"""
    print("\n" + "=" * 70)
    print("FINAL RESULTS SUMMARY")
    print("=" * 70)

    summary_files = []
    possible_paths = ['.', 'tests', './tests']

    # Auto-detect all TEST_*.txt
    for path in possible_paths:
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.startswith("TEST_") and f.endswith(".txt"):
                    full_path = os.path.join(path, f)
                    if full_path not in summary_files and os.path.exists(full_path):
                        summary_files.append(full_path)

    # Definiši željeni redosled - prvo glavni testovi
    priority_order = [
        "TEST_BASIC_RESULTS.txt",
        "TEST_SPELLING_RESULTS.txt",
        "TEST_GRAMMAR_RESULTS.txt",
        "TEST_CONTEXTUAL_RESULTS.txt"
    ]

    # Grupiši fajlove po prioritetu
    priority_files = []
    other_files = []

    for filepath in summary_files:
        filename = os.path.basename(filepath)
        if filename in priority_order:
            priority_files.append((filename, filepath))
        else:
            other_files.append((filename, filepath))

    # Sortiraj priority files po definisanom redosledu
    priority_files.sort(key=lambda x: priority_order.index(x[0]))
    # Sortiraj other files po imenu
    other_files.sort(key=lambda x: x[0])

    # Kombinuj listu
    all_files = priority_files + other_files

    # Prikazi header tabele
    print(f"\n{'TEST FILE':<35} {'TOTAL':<8} {'PASSED':<8} {'FAILED':<8} {'SUCCESS':<10}")
    print("-" * 75)

    total_all = 0
    passed_all = 0
    failed_all = 0

    # Prikazi rezultate za svaki fajl
    for filename, filepath in all_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

                # Ekstraktuj podatke iz sadržaja fajla
                total = extract_value(content, "TOTAL:")
                passed = extract_value(content, "PASSED:")
                failed = extract_value(content, "FAILED:")
                success_rate = extract_value(content, "SUCCESS:", "%")

                # Ako nema success rate, izračunaj
                if success_rate is None and total is not None and passed is not None:
                    success_rate = round((passed / total) * 100, 2)

                # Prikazi u tabeli
                if total is not None and passed is not None:
                    # Koristi tačno ime fajla umesto skraćenog
                    display_name = filename

                    # Formatiraj success rate sa bojama
                    success_str = f"{success_rate}%"
                    if success_rate == 100:
                        success_str = f"✅ {success_rate}%"
                    elif success_rate >= 90:
                        success_str = f"🟢 {success_rate}%"
                    elif success_rate >= 80:
                        success_str = f"🟡 {success_rate}%"
                    else:
                        success_str = f"🔴 {success_rate}%"

                    failed_display = failed if failed else 0
                    print(f"{display_name:<35} {total:<8} {passed:<8} {failed_display:<8} {success_str:<10}")

                    # Akumuliraj za ukupno
                    total_all += total
                    passed_all += passed
                    if failed:
                        failed_all += failed

        except Exception as e:
            print(f"❌ {filename}: ERROR reading file ({e})")

    # Prikazi ukupnu statistiku
    print("-" * 75)
    if total_all > 0:
        overall_success = round((passed_all / total_all) * 100, 2)

        overall_str = f"{overall_success}%"
        if overall_success == 100:
            overall_str = f"🎉 {overall_success}%"
        elif overall_success >= 90:
            overall_str = f"✅ {overall_success}%"
        elif overall_success >= 80:
            overall_str = f"⚠️  {overall_success}%"
        else:
            overall_str = f"❌ {overall_success}%"

        print(f"{'OVERALL':<35} {total_all:<8} {passed_all:<8} {failed_all:<8} {overall_str:<10}")

        # Status poruka
        print("\n" + "=" * 70)
        print("📊 FINAL STATUS:")
        if overall_success == 100:
            print("🎉 EXCELLENT - All tests passed! Ready for production! 🚀")
        elif overall_success >= 90:
            print("✅ VERY GOOD - Production ready with minor improvements")
        elif overall_success >= 80:
            print("⚠️  GOOD - Minor improvements needed before production")
        elif overall_success >= 70:
            print("🔶 FAIR - Some attention required")
        else:
            print("🔴 NEEDS WORK - Significant improvements needed")
    else:
        print("❌ No test results found!")

    print("=" * 70)


def collect_files():
    """Organizuje kod u 5 tekstualnih fajlova u code_and_tests_collected folderu"""

    # Definiši strukturu fajlova
    CODE_STRUCTURE = {
        "1_CODE.txt": [
            "app.py",
            "correctors/base_corrector.py",
            "correctors/spelling_corrector.py",
            "correctors/grammar_corrector.py",
            "correctors/contextual_corrector.py",
            "simple_error_handler.py",
            "auth.py"
        ],
        "2_MAIN_TESTS.txt": [
            "tests/test_basic.py",
            "tests/test_spelling.py",
            "tests/test_grammar.py",
            "tests/test_contextual_spelling.py"
        ],
        "3_MAIN_TESTS_RESULTS.txt": [
            "TEST_BASIC_RESULTS.txt",
            "TEST_SPELLING_RESULTS.txt",
            "TEST_GRAMMAR_RESULTS.txt",
            "TEST_CONTEXTUAL_RESULTS.txt"
        ],
        "4_SPEC_TESTS.txt": [
            "tests/test_edge_cases.py",
            "tests/test_i_capitalization.py",
            "tests/test_grammar_heuristics.py",
            "tests/production_benchmark.py",
            "tests/test_word_order_fix.py"
        ],
        "5_SPEC_TESTS_RESULTS.txt": [
            "TEST_EDGE_CASES_RESULTS.txt",
            "TEST_APOSTROPHE_RESULTS.txt",
            "GRAMMAR_HEURISTICS_TEST.json",
            "I_CAPITALIZATION_TEST.json"
        ]
    }

    root = os.getcwd()
    output_dir = os.path.join(root, "code_and_tests_collected")

    # Kreiraj output direktorijum
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📦 CREATING ORGANIZED FILES IN: code_and_tests_collected/")
    print("-" * 50)

    # Kreiraj tekstualne fajlove
    for output_file, source_files in CODE_STRUCTURE.items():
        output_path = os.path.join(output_dir, output_file)

        print(f"\n📄 Creating {output_file}:")
        print("-" * 30)

        with open(output_path, "w", encoding="utf-8") as out_file:
            for file_path in source_files:
                source_path = os.path.join(root, file_path)

                if not os.path.exists(source_path):
                    print(f"❌ [NOT FOUND] {file_path}")
                    out_file.write(f"\n\n{'=' * 70}\n")
                    out_file.write(f"FILE: {file_path} - NOT FOUND\n")
                    out_file.write(f"{'=' * 70}\n\n")
                    continue

                try:
                    with open(source_path, "r", encoding="utf-8", errors="ignore") as src:
                        content = src.read()

                    out_file.write(f"\n\n{'=' * 70}\n")
                    out_file.write(f"FILE: {file_path}\n")
                    out_file.write(f"{'=' * 70}\n\n")
                    out_file.write(content)

                    print(f"✅ [ADDED] {file_path}")

                except Exception as e:
                    print(f"❌ [ERROR] {file_path}: {e}")
                    out_file.write(f"\n\n{'=' * 70}\n")
                    out_file.write(f"FILE: {file_path} - ERROR: {e}\n")
                    out_file.write(f"{'=' * 70}\n\n")

    # Kreiraj CSV fajl sa rezultatima testova
    create_test_results_csv(output_dir)

    print(f"\n🎉 Successfully created organized files in: code_and_tests_collected/")


def create_test_results_csv(output_dir):
    """Kreira CSV fajl sa rezultatima svih testova"""
    import re

    csv_path = os.path.join(output_dir, "TEST_RESULTS_SUMMARY.csv")

    print(f"\n📊 Creating TEST_RESULTS_SUMMARY.csv:")
    print("-" * 30)

    # Prikupi sve TEST_*.txt fajlove
    summary_files = []
    possible_paths = ['.', 'tests', './tests']

    for path in possible_paths:
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.startswith("TEST_") and f.endswith(".txt"):
                    full_path = os.path.join(path, f)
                    if full_path not in summary_files and os.path.exists(full_path):
                        summary_files.append(full_path)

    test_results = []
    total_all = 0
    passed_all = 0
    failed_all = 0

    for filepath in summary_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Ekstraktuj podatke
            total = extract_value(content, "TOTAL:")
            passed = extract_value(content, "PASSED:")
            failed = extract_value(content, "FAILED:")
            success_rate = extract_value(content, "SUCCESS:", "%")

            if success_rate is None and total is not None and passed is not None:
                success_rate = round((passed / total) * 100, 2)

            if total is not None and passed is not None:
                test_results.append({
                    'test_file': os.path.basename(filepath),
                    'total_tests': total,
                    'passed_tests': passed,
                    'failed_tests': failed if failed else 0,
                    'success_rate': success_rate,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

                total_all += total
                passed_all += passed
                if failed:
                    failed_all += failed

                print(f"✅ [CSV ADDED] {os.path.basename(filepath)}")

        except Exception as e:
            print(f"❌ [CSV ERROR] {os.path.basename(filepath)}: {e}")

    # Dodaj ukupni red
    if total_all > 0:
        overall_success = round((passed_all / total_all) * 100, 2)
        test_results.append({
            'test_file': 'OVERALL',
            'total_tests': total_all,
            'passed_tests': passed_all,
            'failed_tests': failed_all,
            'success_rate': overall_success,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    # Zapiši CSV fajl
    if test_results:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['test_file', 'total_tests', 'passed_tests', 'failed_tests', 'success_rate', 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in test_results:
                writer.writerow(result)

        print(f"✅ [CSV CREATED] TEST_RESULTS_SUMMARY.csv")
        print(f"   📈 Records: {len(test_results)}")
    else:
        print("❌ [CSV EMPTY] No test results found")


def main():
    # Pokreni testove
    tests_completed = run_all_tests()

    # Organizuj fajlove
    print("\n" + "=" * 70)
    print("STARTING FILE COLLECTION")
    print("=" * 70)

    collect_files()

    # Prikaži finalne rezultate na SAMOM KRAJU
    display_final_results_summary()

    print("\n" + "=" * 70)
    print("COMPLETE! All tests run and files collected.")
    print("=" * 70)


if __name__ == "__main__":
    main()