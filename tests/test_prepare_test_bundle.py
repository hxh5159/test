"""Pure synthetic extraction checks, with no archived program execution."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_test_bundle import prepare


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base/"repo"
        self.root.mkdir()
        self.archive = self.root/"example.zip"
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr("env_open_models.sh", "export TEST_ONLY=1\n")
            archive.writestr("nested/notes.txt", "synthetic data\n")
        self.manifest = {"packages": {"4090": {"status": "current", "file": "example.zip",
            "sha256": hashlib.sha256(self.archive.read_bytes()).hexdigest(), "extract_dir": "unpacked"}}}
        self.save()

    def save(self):
        (self.root/"packages.json").write_text(json.dumps(self.manifest))

    def tearDown(self):
        self.tmp.cleanup()

    def test_prepare_and_repeat_preserve_existing_result(self):
        first = prepare("4090", repository_root=self.root)
        target = Path(first["extracted_to"])
        (target/"results").mkdir()
        (target/"results"/"keep.txt").write_text("keep")
        self.assertEqual(prepare("4090", repository_root=self.root)["status"], "already_prepared_files_unchanged")
        self.assertEqual((target/"results"/"keep.txt").read_text(), "keep")
        self.assertEqual(first["model_physics_or_api_calls"], 0)

    def test_empty_existing_directory_is_accepted(self):
        (self.base/"unpacked").mkdir()
        self.assertEqual(prepare("4090", repository_root=self.root)["status"], "prepared")

    def test_wrong_checksum_or_missing_archive_creates_no_target(self):
        self.manifest["packages"]["4090"]["sha256"] = "0"*64
        self.save()
        with self.assertRaises(ValueError):
            prepare("4090", repository_root=self.root)
        self.assertFalse((self.base/"unpacked").exists())
        self.archive.unlink()
        with self.assertRaises(FileNotFoundError):
            prepare("4090", repository_root=self.root)

    def test_modified_or_unowned_directory_is_not_overwritten(self):
        target = self.base/"unpacked"
        target.mkdir()
        (target/"keep.txt").write_text("keep")
        with self.assertRaises(FileExistsError):
            prepare("4090", repository_root=self.root)
        owned = self.base/"owned"
        prepare("4090", owned, repository_root=self.root)
        (owned/"nested"/"notes.txt").write_text("modified")
        with self.assertRaises(FileExistsError):
            prepare("4090", owned, repository_root=self.root)
        self.assertEqual((owned/"nested"/"notes.txt").read_text(), "modified")

    def test_unsafe_archive_paths_are_rejected_before_extraction(self):
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr("../escape.txt", "bad")
        self.manifest["packages"]["4090"]["sha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.save()
        with self.assertRaises(ValueError):
            prepare("4090", repository_root=self.root)
        self.assertFalse((self.base/"unpacked").exists())


if __name__ == "__main__":
    unittest.main()
