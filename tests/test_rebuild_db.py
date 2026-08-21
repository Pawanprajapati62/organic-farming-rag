import tempfile
from pathlib import Path
import unittest

from rebuild_db import activate_database


class AtomicDatabaseSwapTests(unittest.TestCase):
    def test_activates_staging_database_and_removes_backup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            vectorstore_dir = Path(temp_dir) / "vectorstore"
            vectorstore_dir.mkdir()
            active_db = vectorstore_dir / "chroma_db"
            staging_db = vectorstore_dir / ".chroma-staging-test"
            active_db.mkdir()
            staging_db.mkdir()
            (active_db / "version.txt").write_text("old", encoding="utf-8")
            (staging_db / "version.txt").write_text("new", encoding="utf-8")

            activate_database(staging_db, active_db)

            self.assertEqual(
                (active_db / "version.txt").read_text(encoding="utf-8"), "new"
            )
            self.assertFalse(any(vectorstore_dir.glob(".chroma-backup-*")))

    def test_restores_active_database_when_activation_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            vectorstore_dir = Path(temp_dir) / "vectorstore"
            vectorstore_dir.mkdir()
            active_db = vectorstore_dir / "chroma_db"
            missing_staging_db = vectorstore_dir / ".chroma-staging-missing"
            active_db.mkdir()
            (active_db / "version.txt").write_text("old", encoding="utf-8")

            with self.assertRaises(FileNotFoundError):
                activate_database(missing_staging_db, active_db)

            self.assertEqual(
                (active_db / "version.txt").read_text(encoding="utf-8"), "old"
            )
            self.assertFalse(any(vectorstore_dir.glob(".chroma-backup-*")))


if __name__ == "__main__":
    unittest.main()
