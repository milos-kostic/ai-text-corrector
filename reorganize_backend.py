import os
import shutil
from pathlib import Path

"""
AUTOMATSKA REORGANIZACIJA BACKEND STRUKTURE
-------------------------------------------
Ova skripta:
  ✔ pravi folder backend/app/
  ✔ premešta app.py → app/main.py
  ✔ premešta auth.py, simple_error_handler.py → app/
  ✔ premešta correctors/ → app/correctors/
  ✔ premešta tests/ → app/tests/
  ✔ pravi folder outputs/ → za sve TEST_*.txt fajlove
  ✔ pravi folder benchmarks/
  ✔ premešta performance* i production* skripte
  ✔ pravi utils/ folder za collect skriptu
  ✔ pravi run.py fajl
  ✔ pravi backup pre reorganizacije

Sigurno za ponovna pokretanja (idempotentno).
"""

print("\n🚀 Starting backend reorganization...\n")

ROOT = Path(os.getcwd())
BACKEND = ROOT / "backend"

if not BACKEND.exists():
    raise RuntimeError("❌ ERROR: Folder 'backend/' ne postoji u root-u projekta!")

# ---------------------------------------------
# 1) Napravi BEZBEDNOSNI BACKUP
# ---------------------------------------------
BACKUP = ROOT / "_backup_before_restructure"

if not BACKUP.exists():
    print("📦 Creating backup folder...")
    shutil.copytree(BACKEND, BACKUP)
    print("✔ Backup saved in:", BACKUP)
else:
    print("ℹ Backup already exists — skipping.")


# ---------------------------------------------
# 2) Kreiraj novu strukturu foldera
# ---------------------------------------------
APP_DIR = BACKEND / "app"
CORRECTORS_DIR = APP_DIR / "correctors"
TESTS_DIR = APP_DIR / "tests"
OUTPUTS_DIR = BACKEND / "outputs"
BENCH_DIR = BACKEND / "benchmarks"
UTILS_DIR = BACKEND / "utils"

for d in [APP_DIR, CORRECTORS_DIR, TESTS_DIR, OUTPUTS_DIR, BENCH_DIR, UTILS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------
# 3) Premeštanje Python fajlova
# ---------------------------------------------

def safe_move(src, dst_dir, rename=None):
    if not src.exists():
        return
    dst = dst_dir / (rename if rename else src.name)
    if not dst.exists():
        shutil.move(str(src), str(dst))


print("📁 Moving top-level Python files...")

safe_move(BACKEND / "app.py", APP_DIR, rename="main.py")
safe_move(BACKEND / "auth.py", APP_DIR)
safe_move(BACKEND / "simple_error_handler.py", APP_DIR)

# ---------------------------------------------
# 4) Premeštanje correctors/
# ---------------------------------------------
if (BACKEND / "correctors").exists():
    for f in (BACKEND / "correctors").iterdir():
        safe_move(f, CORRECTORS_DIR)
    shutil.rmtree(BACKEND / "correctors", ignore_errors=True)


# ---------------------------------------------
# 5) Premeštanje testova
# ---------------------------------------------
if (BACKEND / "tests").exists():
    for f in (BACKEND / "tests").iterdir():
        safe_move(f, TESTS_DIR)
    shutil.rmtree(BACKEND / "tests", ignore_errors=True)


# ---------------------------------------------
# 6) Premeštanje test rezultata → outputs/
# ---------------------------------------------
for f in BACKEND.iterdir():
    if f.is_file() and (
        f.name.startswith("TEST_") and f.name.endswith(".txt")
        or f.name.endswith("_RESULTS.txt")
        or f.name.endswith(".json")
    ):
        safe_move(f, OUTPUTS_DIR)


# ---------------------------------------------
# 7) Premeštanje benchmark fajlova
# ---------------------------------------------
for f in BACKEND.iterdir():
    if f.is_file() and (
        f.name.startswith("performance") or f.name.startswith("production")
    ):
        safe_move(f, BENCH_DIR)


# ---------------------------------------------
# 8) Premeštanje collect skripte u utils/
# ---------------------------------------------
if (BACKEND / "_collect.py").exists():
    safe_move(BACKEND / "_collect.py", UTILS_DIR)


# ---------------------------------------------
# 9) Kreiranje run.py ako ne postoji
# ---------------------------------------------
RUN_FILE = BACKEND / "run.py"

if not RUN_FILE.exists():
    RUN_FILE.write_text(
        "from app.main import app\n\n"
        "if __name__ == '__main__':\n"
        "    from waitress import serve\n"
        "    serve(app, host='0.0.0.0', port=5000)\n"
    )
    print("🆕 Created run.py")


# ---------------------------------------------
# 10) Gotovo!
# ---------------------------------------------
print("\n🎉 Backend successfully reorganized!")
print("📦 Backup folder:", BACKUP)
print("📂 New backend structure ready.\n")
