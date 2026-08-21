"""Safely rebuild the Chroma database without interrupting the live database."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid


ROOT_DIR = Path(__file__).resolve().parent
DB_PATH = Path(
    os.getenv("VECTOR_DB_PATH", ROOT_DIR / "vectorstore" / "chroma_db")
).resolve()
VECTORSTORE_DIR = DB_PATH.parent


def remove_staging_directory(path: Path, parent_dir: Path = VECTORSTORE_DIR) -> None:
    """Remove only a staging or backup directory created inside vectorstore."""
    if path.parent != parent_dir or not path.name.startswith(".chroma-"):
        raise ValueError(f"Refusing to remove an unexpected path: {path}")
    if path.exists():
        shutil.rmtree(path)


def activate_database(staging_path: Path, database_path: Path) -> None:
    """Atomically replace the active database, restoring it if the swap fails."""
    backup_path = database_path.with_name(f".chroma-backup-{uuid.uuid4().hex}")
    previous_database_exists = database_path.exists()

    try:
        if previous_database_exists:
            database_path.replace(backup_path)
        staging_path.replace(database_path)
    except Exception:
        if previous_database_exists and backup_path.exists() and not database_path.exists():
            backup_path.replace(database_path)
        raise
    else:
        if backup_path.exists():
            remove_staging_directory(backup_path, database_path.parent)


def rebuild_database() -> None:
    VECTORSTORE_DIR.mkdir(exist_ok=True)
    staging_path = Path(
        tempfile.mkdtemp(prefix=".chroma-staging-", dir=VECTORSTORE_DIR)
    )
    venv_python = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
    python_exec = str(venv_python) if venv_python.exists() else sys.executable
    env = os.environ.copy()
    env["VECTOR_DB_PATH"] = str(staging_path)

    print("=" * 60)
    print("Rebuilding Chroma Vector Database")
    print("=" * 60)
    print(f"\nBuilding and validating a replacement database in:\n{staging_path}\n")

    try:
        result = subprocess.run(
            [python_exec, str(ROOT_DIR / "src" / "create_vector_db.py")],
            cwd=ROOT_DIR,
            env=env,
        )
        if result.returncode != 0:
            raise RuntimeError("The replacement database build failed validation.")

        activate_database(staging_path, DB_PATH)
    except Exception:
        remove_staging_directory(staging_path)
        print("\nDatabase rebuild failed. The existing knowledge base was preserved.")
        raise

    print("\n" + "=" * 60)
    print("Chroma Database Rebuilt Successfully")
    print("=" * 60)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rebuild_database()

