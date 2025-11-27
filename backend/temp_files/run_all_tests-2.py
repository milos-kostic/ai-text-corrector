# run_all_tests - origin (with auto final summary for all TEST_*.txt)
import subprocess
import sys
import os
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

    # -----------------------------------------------------------------
    # FINAL RESULTS SUMMARY (AUTO-DETECT ALL TEST_*.txt FILES)
    # -----------------------------------------------------------------
    print("\nFINAL RESULTS SUMMARY:")
    print("=" * 30)

    summary_files = []

    # Auto-detect all TEST_*.txt
    for path in possible_paths:
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.startswith("TEST_") and f.endswith(".txt"):
                    if f not in summary_files:
                        summary_files.append(f)

    summary_files = sorted(summary_files)

    for filename in summary_files:
        file_found = False

        for path in possible_paths:
            full_path = os.path.join(path, filename)
            if os.path.exists(full_path):
                file_found = True
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        for line in f:
                            low = line.lower()
                            if ("total:" in low and "passed:" in low and "success" in low):
                                print(f"📊 {filename}: {line.strip()}")
                                break
                except Exception as e:
                    print(f"❌ {filename}: ERROR reading file ({e})")
                break

        if not file_found:
            print(f"❌ {filename}: NOT FOUND")

    print("\n" + "=" * 70)


# ---------------------------------------------------------
# FILE COLLECTION (unchanged)
# ---------------------------------------------------------

def collect_files():
    OUTPUT_FILE = "_ALL_CODE_COLLECTED.txt"

    FILES_TO_COLLECT = [
        "app.py",
        "correctors/base_corrector.py",
        "correctors/spelling_corrector.py",
        "correctors/grammar_corrector.py",
        "correctors/contextual_corrector.py",
        "simple_error_handler.py",
        "auth.py",
        "tests/test_basic.py",
        "tests/test_spelling.py",
        "tests/test_grammar.py",
        "tests/test_edge_cases.py",
        "tests/test_contextual_spelling.py",
        "tests/test_i_capitalization.py",
        "tests/test_grammar_heuristics.py",
        "tests/production_benchmark.py",
        "tests/test_word_order_fix.py",
        "TEST_BASIC_RESULTS.txt",
        "TEST_SPELLING_RESULTS.txt",
        "TEST_GRAMMAR_RESULTS.txt",
        "TEST_EDGE_CASES_RESULTS.txt",
        "TEST_CONTEXTUAL_RESULTS.txt",
        "GRAMMAR_HEURISTICS_TEST.json",
        "I_CAPITALIZATION_TEST.json",
    ]

    root = os.getcwd()
    output_path = os.path.join(root, OUTPUT_FILE)

    print(f"\n📦 COLLECTING ALL FILES INTO: {OUTPUT_FILE}")
    print("-" * 50)

    with open(output_path, "w", encoding="utf-8") as out:

        for file_path in FILES_TO_COLLECT:
            abs_path = os.path.join(root, file_path)

            out.write("\n\n" + "-" * 70 + "\n")
            out.write(f"FILE: {file_path}\n")
            out.write("-" * 70 + "\n\n")

            if not os.path.exists(abs_path):
                out.write(f"[FILE NOT FOUND] {file_path}\n")
                print(f"❌ [NOT FOUND] {file_path}")
                continue

            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    out.write(f.read())
                print(f"✅ [COLLECTED] {file_path}")
            except Exception as e:
                out.write(f"[ERROR READING FILE] {e}\n")
                print(f"❌ [ERROR] {file_path}: {e}")

    print(f"\n🎉 Successfully created: {OUTPUT_FILE}")


def main():
    run_all_tests()

    print("\n" + "=" * 70)
    print("STARTING FILE COLLECTION")
    print("=" * 70)

    collect_files()

    print("\n" + "=" * 70)
    print("COMPLETE! All tests run and files collected.")
    print("=" * 70)


if __name__ == "__main__":
    main()
