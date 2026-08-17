from pathlib import Path
import shutil
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Project Root
ROOT_DIR = Path(__file__).resolve().parent

# Chroma DB Path
DB_PATH = ROOT_DIR / "vectorstore" / "chroma_db"

# Virtual environment python check
venv_python = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
python_exec = str(venv_python) if venv_python.exists() else sys.executable

print("=" * 60)
print("Rebuilding Chroma Vector Database")
print("=" * 60)

# Delete existing database
if DB_PATH.exists():
    print(f"\nDeleting old database:\n{DB_PATH}")
    shutil.rmtree(DB_PATH)
    print("Old database deleted.")
else:
    print("\nNo existing database found.")

# Create vector database again
print("\nCreating new vector database...\n")

result = subprocess.run(
    [python_exec, str(ROOT_DIR / "src" / "create_vector_db.py")],
    cwd=ROOT_DIR
)

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("Chroma Database Rebuilt Successfully!")
    print("=" * 60)
else:
    print("\nFailed to rebuild database.")
