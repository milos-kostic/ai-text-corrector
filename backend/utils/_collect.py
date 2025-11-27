import os

OUTPUT_FILE = "_ALL_CODE_COLLECTED.txt"

# Lista fajlova koje ćemo skupiti
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
    "tests/test_contextual_spelling.py",
    "TEST_BASIC_RESULTS.txt",
    "TEST_SPELLING_RESULTS.txt",
    "TEST_GRAMMAR_RESULTS.txt",
    "TEST_CONTEXTUAL_RESULTS.txt",
]


def collect_files():
    root = os.getcwd()
    output_path = os.path.join(root, OUTPUT_FILE)

    # 🔥 OVA LINIJA UVEK BRIŠE STARI FAJL I KREIRA NOVI
    # Otvaranje sa "w" MODOM znači: truncate / isprazni fajl ako postoji.
    with open(output_path, "w", encoding="utf-8") as out:

        for file_path in FILES_TO_COLLECT:
            abs_path = os.path.join(root, file_path)

            out.write("\n\n" + "-" * 70 + "\n")
            out.write(f"FILE: {file_path}\n")
            out.write("-" * 70 + "\n\n")

            if not os.path.exists(abs_path):
                out.write(f"[FILE NOT FOUND] {file_path}\n")
                continue

            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"[ERROR READING FILE] {e}\n")

    print(f"\n📄 Successfully created: {OUTPUT_FILE}\n")


if __name__ == "__main__":
    collect_files()
