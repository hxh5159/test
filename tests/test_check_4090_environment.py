"""Synthetic filesystem and subprocess tests; no GPU, models, network or physics."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "check_4090_environment.py"
SPEC = importlib.util.spec_from_file_location("environment_doctor", SCRIPT)
doctor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(doctor)


class EnvironmentDoctorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "bundle"
        self.models = self.base / "models"
        self.root.mkdir()
        for name in doctor.REQUIRED_FILES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if name.endswith(".py"):
                # Any accidental import or execution in the paths phase fails.
                path.write_text('raise RuntimeError("Private science must not execute")\n', encoding="utf-8")
            elif name.endswith(".json"):
                path.write_text('{}\n', encoding="utf-8")
            else:
                path.write_text('# synthetic fixture\n', encoding="utf-8")
        self.update_manifest()
        for name in doctor.MODEL_NAMES:
            model = self.models / name
            model.mkdir(parents=True)
            (model / "config.json").write_text('{"model_type":"fixture"}', encoding="utf-8")
            (model / "tokenizer_config.json").write_text('{}', encoding="utf-8")
            (model / "tokenizer.json").write_text('{}', encoding="utf-8")
            header = json.dumps({"weight": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]}}).encode()
            (model / "model.safetensors").write_bytes(struct.pack("<Q", len(header)) + header + b"\0" * 4)
        self.cpu = {"ok": True, "python": [3, 12, 10], "numpy": "2.1.3", "scipy": "1.15.3",
                    "rift_numerics_origin": str(self.root / "rift_numerics/__init__.py"),
                    "rift_numerics_executed": False}
        self.gpu = {"ok": True, "python": [3, 12, 10], "vllm": "0.32.0+cu129", "torch": "2.11.0+cu129",
                    "torch_distribution": "2.11.0+cu129", "cuda_runtime": "12.9", "visible_device_count": 4,
                    "imported_extensions": ["vllm._C_stable_libtorch", "vllm._moe_C_stable_libtorch"],
                    "devices": [{"index": i, "name": "NVIDIA GeForce RTX 4090", "total_memory_bytes": 48 * 2**30,
                                 "compute_capability": [8, 9], "bf16_ok": True} for i in range(4)]}

    def update_manifest(self):
        files = {}
        for name in doctor.REQUIRED_FILES:
            if name != "PRIVATE_PACKAGE_MANIFEST.json":
                raw = (self.root / name).read_bytes()
                files[name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        (self.root / "PRIVATE_PACKAGE_MANIFEST.json").write_text(json.dumps({"files": files}), encoding="utf-8")

    def add_environments(self):
        for name in (".venv-trial", ".venv-vllm"):
            python = self.root / name / "bin/python"
            python.parent.mkdir(parents=True)
            python.write_text('#!/usr/bin/env python3\n', encoding="utf-8")
            python.chmod(0o755)

    def fake_run(self, command, **kwargs):
        if command[0] == "nvidia-smi":
            return subprocess.CompletedProcess(command, 0, "0, NVIDIA GeForce RTX 4090, 570.195.03, 49140\n", "")
        self.assertIn(command[0], [str(self.root / ".venv-trial/bin/python"), str(self.root / ".venv-vllm/bin/python")])
        self.assertEqual(kwargs["cwd"], self.root)
        self.assertGreater(kwargs["timeout"], 0)
        self.assertEqual(kwargs["env"]["HF_HUB_OFFLINE"], "1")
        self.assertEqual(kwargs["env"]["PYTHONPATH"], str(self.root))
        self.assertNotIn("VLLM_API_KEY", kwargs["env"])
        if command[2] == doctor.CPU_PROBE:
            payload = self.cpu
        elif command[2] == doctor.GPU_PROBE:
            payload = self.gpu
        else:
            self.assertEqual(command[2], doctor.HELP_PROBE)
            self.assertEqual(command[-2:], [str(self.root / "open_model_calibration.py"), "--help"])
            return subprocess.CompletedProcess(command, 0, "usage: open_model_calibration.py [-h]\n", "")
        return subprocess.CompletedProcess(command, 0, doctor.MARKER + json.dumps(payload) + "\n", "")

    def checks(self, report):
        return {item["name"]: item for item in report["checks"]}

    def run_main(self, *extra):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = doctor.main(["--test-root", str(self.root), "--model-root", str(self.models), *extra])
        return code, json.loads(stdout.getvalue()), stderr.getvalue()

    def test_paths_checks_extracted_files_without_executing_sources_or_gpu(self):
        with patch.object(doctor.subprocess, "run") as run:
            report = doctor.build_report(self.root, self.models, "paths")
        run.assert_not_called()
        self.assertEqual(report["status"], "paths_checked")
        checks = self.checks(report)
        self.assertEqual(checks["trial_python_path"]["status"], "not_installed")
        self.assertTrue(checks["extracted_bundle"]["manifest_hashes_verified"])
        self.assertGreater(checks["extracted_bundle"]["compiled_without_execution"], 10)
        self.assertFalse((self.root / "results").exists())
        self.assertFalse((self.root / "__pycache__").exists())

    def test_missing_environment_never_uses_base_python(self):
        with patch.object(doctor.subprocess, "run") as run:
            report = doctor.build_report(self.root, self.models)
        run.assert_not_called()
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(self.checks(report)["installed_probes"]["status"], "skipped")

    def test_corrupt_or_uncompiled_bundle_blocks_all_installed_probes(self):
        self.add_environments()
        path = self.root / "rift_numerics/rollout.py"
        for update_manifest in (False, True):
            with self.subTest(updated_manifest=update_manifest):
                path.write_text('def broken(:\n', encoding="utf-8")
                if update_manifest:
                    self.update_manifest()
                with patch.object(doctor.subprocess, "run") as run:
                    report = doctor.build_report(self.root, self.models)
                self.assertEqual(report["status"], "blocked")
                self.assertEqual(self.checks(report)["extracted_bundle"]["status"], "fail")
                run.assert_not_called()

    def test_truncated_header_and_missing_shard_block(self):
        model = self.models / doctor.MODEL_NAMES[0]
        (model / "model.safetensors").write_bytes(struct.pack("<Q", 500) + b"{}")
        report = doctor.build_report(self.root, self.models, "paths")
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(self.checks(report)[f"model_files:{doctor.MODEL_NAMES[0]}"]["status"], "fail")
        (model / "model.safetensors.index.json").write_text('{"weight_map":{"weight":"missing.safetensors"}}')
        report = doctor.build_report(self.root, self.models, "paths")
        self.assertEqual(report["status"], "blocked")

    def test_index_cannot_traverse_outside_model_directory(self):
        model = self.models / doctor.MODEL_NAMES[0]
        (model / "model.safetensors.index.json").write_text('{"weight_map":{"weight":"../outside.safetensors"}}')
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            doctor.inspect_model(model)

    def test_installed_ready_requires_real_probe_evidence_and_preserves_allocation(self):
        self.add_environments()
        with patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "GPU-a,GPU-b,GPU-c,GPU-d", "VLLM_API_KEY": "secret"}), \
                patch.object(doctor.subprocess, "run", side_effect=self.fake_run) as run:
            report = doctor.build_report(self.root, self.models)
        self.assertEqual(report["status"], "ready_for_model_service_checks")
        self.assertEqual(run.call_count, 4)
        for call in run.call_args_list:
            self.assertEqual(call.kwargs["env"]["CUDA_VISIBLE_DEVICES"], "GPU-a,GPU-b,GPU-c,GPU-d")
        inventory = self.checks(report)["driver_inventory"]["inventory"]
        self.assertEqual(inventory[0]["driver_version"], "570.195.03")
        self.assertEqual(report["model_or_api_or_physics_calls"], 0)
        self.assertIsNone(report["scientific_score"])

    def test_zero_exit_without_structured_evidence_is_blocked(self):
        self.add_environments()
        with patch.object(doctor.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "all good", "")):
            report = doctor.build_report(self.root, self.models)
        self.assertEqual(report["status"], "blocked")

    def test_wrong_python_or_incomplete_gpu_evidence_is_blocked(self):
        self.add_environments()
        self.cpu["python"] = [3, 14, 0]
        self.gpu["devices"][2]["bf16_ok"] = False
        with patch.object(doctor.subprocess, "run", side_effect=self.fake_run):
            report = doctor.build_report(self.root, self.models)
        self.assertEqual(report["status"], "blocked")
        checks = self.checks(report)
        self.assertEqual(checks["trial_imports"]["status"], "fail")
        self.assertEqual(checks["gpu_runtime"]["status"], "fail")
        self.assertNotIn("calibration_cli_help", checks)

    def test_cli_zero_exit_without_help_is_blocked(self):
        self.add_environments()
        def fake(command, **kwargs):
            if len(command) > 2 and command[2] == doctor.HELP_PROBE:
                return subprocess.CompletedProcess(command, 0, "", "")
            return self.fake_run(command, **kwargs)
        with patch.object(doctor.subprocess, "run", side_effect=fake):
            report = doctor.build_report(self.root, self.models)
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(self.checks(report)["calibration_cli_help"]["status"], "fail")

    def test_driver_timeout_is_diagnostic_but_gpu_timeout_blocks(self):
        self.add_environments()
        def fake(command, **kwargs):
            if command[0] == "nvidia-smi" or (len(command) > 2 and command[2] == doctor.GPU_PROBE):
                raise subprocess.TimeoutExpired(command, kwargs["timeout"])
            return self.fake_run(command, **kwargs)
        with patch.object(doctor.subprocess, "run", side_effect=fake):
            report = doctor.build_report(self.root, self.models, timeout=0.5)
        self.assertEqual(report["status"], "blocked")
        checks = self.checks(report)
        self.assertEqual(checks["driver_inventory"]["status"], "warning")
        self.assertIn("0.5s", checks["gpu_runtime"]["error"])
        self.assertIsNone(report["scientific_score"])

    def test_structured_gpu_failure_retains_installation_or_driver_category(self):
        self.add_environments()
        for category in ("installation", "driver_runtime"):
            with self.subTest(category=category):
                self.gpu = {"ok": False, "category": category, "error": "synthetic infrastructure failure"}
                with patch.object(doctor.subprocess, "run", side_effect=self.fake_run):
                    report = doctor.build_report(self.root, self.models)
                self.assertEqual(report["status"], "blocked")
                self.assertEqual(self.checks(report)["gpu_runtime"]["category"], category)

    def test_plan_and_check_only_are_paths_only_and_save_new_reports(self):
        for alias in ("--plan", "--check-only"):
            with self.subTest(alias=alias), patch.object(doctor.subprocess, "run") as run:
                code, report, _ = self.run_main(alias)
                self.assertEqual(code, 0)
                self.assertEqual(report["status"], "paths_checked")
                run.assert_not_called()
                persisted = json.loads(Path(report["report_path"]).read_text(encoding="utf-8"))
                self.assertEqual(persisted, report)

    def test_existing_report_is_preserved_and_cannot_report_ready(self):
        path = self.base / "existing.json"
        original = b'{"previous":"keep"}'
        path.write_bytes(original)
        code, report, _ = self.run_main("--phase", "paths", "--report", str(path))
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(self.checks(report)["report_write"]["status"], "fail")

    def test_report_write_failure_overrides_ready_result(self):
        self.add_environments()
        with patch.object(doctor.subprocess, "run", side_effect=self.fake_run), \
                patch.object(doctor, "save_new_report", side_effect=OSError("disk full")):
            code, report, _ = self.run_main()
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "blocked")
        self.assertIn("disk full", self.checks(report)["report_write"]["error"])

    def test_missing_testroot_is_not_created_by_default_report(self):
        self.root = self.base / "absent"
        code, report, _ = self.run_main("--phase", "paths")
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "blocked")
        self.assertFalse(self.root.exists())

    def test_embedded_child_programs_compile_and_block_socket_connections(self):
        for source in (doctor.CPU_PROBE, doctor.GPU_PROBE, doctor.HELP_PROBE):
            compile(source, "<probe>", "exec")
            self.assertIn('sys.addaudithook(_deny_network)', source)
        self.assertEqual(doctor.DEFAULT_TEST_ROOT, SCRIPT.parent.parent / "shore-organizer-4090-test-20261101")


if __name__ == "__main__":
    unittest.main()
