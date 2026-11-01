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

    def replace_archive(self, files):
        with zipfile.ZipFile(self.archive, "w") as archive:
            for name, content in files.items():
                archive.writestr(name, content)
        self.manifest["packages"]["4090"]["sha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.save()

    def snapshot(self, target):
        return {str(path.relative_to(target)): path.read_bytes()
                for path in target.rglob("*") if path.is_file()}

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

    def test_refresh_updates_sources_and_preserves_environment_results_and_cache(self):
        target = Path(prepare("4090", repository_root=self.root)["extracted_to"])
        extras = {".venv-trial/pyvenv.cfg": "existing trial environment",
                  ".venv-vllm/pyvenv.cfg": "existing vllm environment",
                  "logs/keep.log": "existing logs", "results/keep.json": "existing result",
                  ".cache/uv/keep.whl": "existing cached wheel"}
        for name, content in extras.items():
            path = target/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        self.replace_archive({"env_open_models.sh": "export TEST_ONLY=2\n",
                              "nested/notes.txt": "synthetic data\n", "tests/new_check.py": "# new source\n"})
        before = self.snapshot(target)
        with self.assertRaises(FileExistsError):
            prepare("4090", repository_root=self.root)
        self.assertEqual(self.snapshot(target), before)
        result = prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(result["status"], "refreshed")
        self.assertEqual(result["source_files_updated"], 2)
        self.assertEqual((target/"env_open_models.sh").read_text(), "export TEST_ONLY=2\n")
        self.assertEqual((target/"tests/new_check.py").read_text(), "# new source\n")
        for name, content in extras.items():
            self.assertEqual((target/name).read_text(), content)
        receipt = json.loads((target/".test-bundle-receipt.json").read_text())
        self.assertEqual(receipt["archive_sha256"], self.manifest["packages"]["4090"]["sha256"])
        self.assertEqual(set(receipt["files"]), {"env_open_models.sh", "nested/notes.txt", "tests/new_check.py"})
        repeat = prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(repeat["status"], "already_prepared_files_unchanged")
        self.assertEqual(repeat["source_files_updated"], 0)

    def test_refresh_rejects_user_modification_before_any_source_is_written(self):
        target = Path(prepare("4090", repository_root=self.root)["extracted_to"])
        (target/"nested/notes.txt").write_text("my edited source")
        self.replace_archive({"env_open_models.sh": "new environment source",
                              "nested/notes.txt": "new notes", "new.txt": "new source"})
        before = self.snapshot(target)
        with self.assertRaises(FileExistsError):
            prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(self.snapshot(target), before)
        self.assertFalse(any(path.name.startswith(".test-bundle-stage-") for path in target.iterdir()))

    def test_refresh_rejects_new_file_collision_even_if_contents_match(self):
        target = Path(prepare("4090", repository_root=self.root)["extracted_to"])
        (target/"new.txt").write_text("new source")
        self.replace_archive({"env_open_models.sh": "new environment source",
                              "nested/notes.txt": "synthetic data\n", "new.txt": "new source"})
        before = self.snapshot(target)
        with self.assertRaises(FileExistsError):
            prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(self.snapshot(target), before)

    def test_refresh_rejects_parent_directory_collision_before_writes(self):
        target = Path(prepare("4090", repository_root=self.root)["extracted_to"])
        (target/"new_directory").write_text("user file")
        self.replace_archive({"env_open_models.sh": "new environment source",
                              "nested/notes.txt": "synthetic data\n", "new_directory/source.py": "new source"})
        before = self.snapshot(target)
        with self.assertRaises(FileExistsError):
            prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(self.snapshot(target), before)

    def test_refresh_rejects_nonempty_directory_without_receipt(self):
        target = self.base/"unpacked"
        target.mkdir()
        (target/"keep.txt").write_text("my unowned file")
        before = self.snapshot(target)
        with self.assertRaises(FileExistsError):
            prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(self.snapshot(target), before)

    def test_refresh_requires_receipt_even_for_missing_or_empty_target(self):
        target = self.base/"unpacked"
        with self.assertRaisesRegex(FileExistsError, "receipt"):
            prepare("4090", repository_root=self.root, refresh=True)
        self.assertFalse(target.exists())
        target.mkdir()
        with self.assertRaisesRegex(FileExistsError, "receipt"):
            prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(list(target.iterdir()), [])

    def test_refresh_rejects_new_source_inside_runtime_directories(self):
        target = Path(prepare("4090", repository_root=self.root)["extracted_to"])
        runtime_directories = (".venv-trial", ".venv-vllm", "venv", "venv-test", "logs", "results", "cache", ".cache")
        for name in runtime_directories:
            (target/name).mkdir()
            (target/name/"keep.txt").write_text("runtime data")
        before = self.snapshot(target)
        for name in runtime_directories:
            with self.subTest(directory=name):
                self.replace_archive({"env_open_models.sh": "new environment source",
                                      "nested/notes.txt": "synthetic data\n", name+"/new_source.py": "new source"})
                with self.assertRaisesRegex(FileExistsError, "environment, log, result or cache"):
                    prepare("4090", repository_root=self.root, refresh=True)
                self.assertEqual(self.snapshot(target), before)

    def test_refresh_refuses_removed_sources_and_keeps_old_receipt(self):
        target = Path(prepare("4090", repository_root=self.root)["extracted_to"])
        self.replace_archive({"env_open_models.sh": "new environment source"})
        before = self.snapshot(target)
        with self.assertRaisesRegex(FileExistsError, "removes source files"):
            prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(self.snapshot(target), before)

    def test_refresh_can_resume_an_old_source_already_at_the_new_hash(self):
        target = Path(prepare("4090", repository_root=self.root)["extracted_to"])
        self.replace_archive({"env_open_models.sh": "new environment source",
                              "nested/notes.txt": "new notes"})
        # Simulate an interrupted refresh after one atomic source replacement
        # but before publication of the new receipt.
        (target/"env_open_models.sh").write_text("new environment source")
        result = prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(result["status"], "refreshed")
        self.assertEqual(result["source_files_updated"], 1)
        self.assertEqual((target/"nested/notes.txt").read_text(), "new notes")

    def test_refresh_validates_new_archive_paths_and_crc_before_writes(self):
        target = Path(prepare("4090", repository_root=self.root)["extracted_to"])
        before = self.snapshot(target)
        for unsafe in ("../escape.txt", ".test-bundle-receipt.json", "nested/../escape.txt"):
            with self.subTest(unsafe=unsafe):
                self.replace_archive({"env_open_models.sh": "new environment source", unsafe: "bad"})
                with self.assertRaises(ValueError):
                    prepare("4090", repository_root=self.root, refresh=True)
                self.assertEqual(self.snapshot(target), before)
        self.replace_archive({"env_open_models.sh": "export TEST_ONLY=2\n", "nested/notes.txt": "synthetic data\n"})
        archive_bytes = self.archive.read_bytes()
        self.archive.write_bytes(archive_bytes.replace(b"export TEST_ONLY=2", b"export TEST_ONLY=3", 1))
        self.manifest["packages"]["4090"]["sha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.save()
        with self.assertRaises((ValueError, zipfile.BadZipFile)):
            prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(self.snapshot(target), before)

    def test_refresh_rejects_receipt_path_escape_before_writes(self):
        target = Path(prepare("4090", repository_root=self.root)["extracted_to"])
        receipt_path = target/".test-bundle-receipt.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["files"]["../outside.txt"] = "0"*64
        receipt_path.write_text(json.dumps(receipt))
        before = self.snapshot(target)
        with self.assertRaises(ValueError):
            prepare("4090", repository_root=self.root, refresh=True)
        self.assertEqual(self.snapshot(target), before)


if __name__ == "__main__":
    unittest.main()
