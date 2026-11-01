"""PRIVATE remote environment checks; standard-library controller, no model loading.

Run on the allocated four-GPU Linux node, after extracting the private bundle.
``--phase paths`` (also ``--plan`` / ``--check-only``) never starts a subprocess
or imports torch, vLLM, or the private scientific modules. The installed phase
uses the two explicit environment Pythons for imports, CLI help, and tiny BF16
matrix products only. It does not install, download, call APIs, or run physics.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import struct
import subprocess
import sys
import tempfile


DEFAULT_TEST_ROOT = Path(__file__).resolve().parent.parent / "shore-organizer-4090-test-20261101"
DEFAULT_MODEL_ROOT = Path("/inspire/hdd/global_public/public_models/Qwen")
MODEL_NAMES = ("Qwen3.8-27B", "Qwen3.5-122B-A10B-FP8")
REQUIRED_FILES = (
    "contest_simulator.py", "contest_world_definitions.json", "claims_truth.json",
    "trial_catalog.py", "trial_console.py", "trial_evaluation.py",
    "expression_candidate.py", "closed_expression_trial.py", "llm_trial_runner.py",
    "open_model_calibration.py", "preflight_open_models.py", "serve_open_models.py",
    "check_open_model_service.py", "env_open_models.sh", "requirements-trials.txt",
    "rift_numerics/__init__.py", "rift_numerics/rollout.py",
    "tests/check_open_model_calibration.py", "tests/check_open_model_preflight.py",
    "tests/check_open_model_launch.py", "tests/check_open_model_service_transport.py",
    "PRIVATE_PACKAGE_MANIFEST.json",
)
LIMIT = 64 * 1024 * 1024
MARKER = "SHORE_CHECK_JSON="

# Block socket connections in children as well as setting offline/cache flags.
# Scientific modules are never imported by this controller.
PROBE_PREFIX = '''import sys, json
def _deny_network(event, args):
    if event in ("socket.connect", "socket.connect_ex", "socket.sendto"):
        raise RuntimeError("Network disabled during environment checks")
sys.addaudithook(_deny_network)
'''

CPU_PROBE = PROBE_PREFIX + '''
import importlib.util
from pathlib import Path
result = {"ok": False, "category": "installation"}
try:
    assert sys.version_info[:2] == (3, 12), "Expected Python 3.12"
    import numpy, scipy, scipy.optimize
    assert numpy.__version__ == "2.1.3", "Expected numpy==2.1.3"
    assert scipy.__version__ == "1.15.3", "Expected scipy==1.15.3"
    spec = importlib.util.find_spec("rift_numerics")
    expected = Path(sys.argv[1]) / "rift_numerics" / "__init__.py"
    assert spec and spec.origin and Path(spec.origin).resolve() == expected.resolve(), "rift_numerics must resolve inside the extracted bundle"
    result.update(ok=True, python=list(sys.version_info[:3]),
        executable=sys.executable, numpy=numpy.__version__, scipy=scipy.__version__,
        rift_numerics_origin=spec.origin, rift_numerics_executed=False)
except Exception as exc:
    result["error"] = type(exc).__name__ + ": " + str(exc)[:2000]
print("SHORE_CHECK_JSON=" + json.dumps(result, allow_nan=False))
raise SystemExit(0 if result["ok"] else 2)
'''

HELP_PROBE = PROBE_PREFIX + '''
import runpy
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
'''

GPU_PROBE = PROBE_PREFIX + '''
import importlib, importlib.metadata as metadata
result = {"ok": False, "category": "installation", "devices": []}
try:
    assert sys.version_info[:2] == (3, 12), "Expected Python 3.12"
    import torch
    vllm_version = metadata.version("vllm")
    assert vllm_version.split("+")[0] == "0.32.0", "Expected vLLM 0.32.0"
    assert torch.version.cuda == "12.9", "Expected the cu129 Torch build"
    extensions = ["vllm._C_stable_libtorch", "vllm._moe_C_stable_libtorch"]
    for name in extensions:
        importlib.import_module(name)
    result.update(python=list(sys.version_info[:3]), executable=sys.executable,
        vllm=vllm_version, torch=torch.__version__,
        torch_distribution=metadata.version("torch"), cuda_runtime=torch.version.cuda,
        imported_extensions=extensions)
    result["category"] = "driver_runtime"
    torch.cuda.init()
    assert torch.cuda.is_available(), "CUDA initialization failed"
    count = torch.cuda.device_count()
    result["visible_device_count"] = count
    assert count == 4, "Expected exactly four allocated visible GPUs"
    for i in range(count):
        props = torch.cuda.get_device_properties(i)
        capability = torch.cuda.get_device_capability(i)
        device = {"index": i, "name": props.name, "total_memory_bytes": props.total_memory,
            "compute_capability": list(capability), "bf16_ok": False}
        result["devices"].append(device)
        assert "4090" in props.name, "Expected RTX 4090 allocation"
        assert capability == (8, 9), "Expected SM 8.9"
        assert props.total_memory >= 40 * 2**30, "Expected 48GB expanded cards (at least 40 GiB)"
        with torch.cuda.device(i):
            x = torch.ones((128, 128), device=f"cuda:{i}", dtype=torch.bfloat16)
            y = x @ x
            torch.cuda.synchronize(i)
            assert bool(torch.all(y == 128).item()), "Small BF16 product disagreed"
            del y, x
        device["bf16_ok"] = True
    result["ok"] = True
except Exception as exc:
    result["error"] = type(exc).__name__ + ": " + str(exc)[:2000]
print("SHORE_CHECK_JSON=" + json.dumps(result, allow_nan=False))
raise SystemExit(0 if result["ok"] else 2)
'''


def parse_json(raw):
    def reject_constant(value):
        raise ValueError(f"Non-finite JSON constant: {value}")
    def unique_fields(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON field")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique_fields, parse_constant=reject_constant)


def read_json(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError("JSON exceeds the 64 MiB inspection bound")
    value = parse_json(raw)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def record(report, name, status, category, **details):
    report["checks"].append(dict(name=name, status=status, category=category, **details))


def attempt(report, name, category, operation):
    try:
        details = operation()
        record(report, name, "pass", category, **(details or {}))
        return True
    except (OSError, ValueError, SyntaxError, KeyError, TypeError, RecursionError) as exc:
        record(report, name, "fail", category, error=f"{type(exc).__name__}: {exc}")
        return False


def inspect_bundle(root):
    if not root.is_dir() or root == Path(root.anchor):
        raise ValueError("test-root must be an existing extracted bundle, not a filesystem root")
    manifest = read_json(root / "PRIVATE_PACKAGE_MANIFEST.json")
    entries = manifest.get("files")
    if not isinstance(entries, dict):
        raise ValueError("Private bundle manifest has no file records")
    compiled = 0
    for name in REQUIRED_FILES:
        path = root / name
        if not path.is_file() or not 0 < path.stat().st_size <= LIMIT:
            raise ValueError(f"Required nonempty extracted file missing/oversized: {name}")
        raw = path.read_bytes()
        if name != "PRIVATE_PACKAGE_MANIFEST.json":
            entry = entries.get(name, {})
            if (not isinstance(entry, dict) or entry.get("sha256") != hashlib.sha256(raw).hexdigest()
                    or entry.get("bytes") != len(raw)):
                raise ValueError(f"Extracted file disagrees with private manifest: {name}")
        if path.suffix == ".py":
            compile(raw, str(path), "exec")  # No execution and no __pycache__ writes.
            compiled += 1
        elif path.suffix == ".json":
            read_json(path)
    return {"required_file_count": len(REQUIRED_FILES), "compiled_without_execution": compiled,
            "manifest_hashes_verified": True}


def inspect_writable(root):
    inspected = []
    for relative in ("logs", "results", "checks", ".cache/uv", ".cache/huggingface", ".cache/vllm"):
        requested = root / relative
        existing = requested
        while not existing.exists() and existing != root:
            existing = existing.parent
        if not existing.is_dir():
            raise ValueError(f"Output/cache path is not a directory: {existing}")
        # Actually create and remove our own tiny temporary file; access() alone
        # cannot establish write access on ACL-managed shared filesystems.
        with tempfile.TemporaryFile(dir=existing) as stream:
            stream.write(b"shore-environment-check\n")
            stream.flush()
        inspected.append({"path": str(requested), "writable_existing_ancestor": str(existing)})
    return {"directories": inspected, "output_directories_created": False}


def inspect_header(path):
    size = path.stat().st_size
    with path.open("rb") as stream:
        prefix = stream.read(8)
        if len(prefix) != 8:
            raise ValueError("Missing safetensors length prefix")
        length = struct.unpack("<Q", prefix)[0]
        if not 2 <= length <= LIMIT or 8 + length > size:
            raise ValueError("Invalid/truncated safetensors header")
        raw = stream.read(length)
    header = parse_json(raw)
    if not isinstance(header, dict):
        raise ValueError("Safetensors header must be an object")
    tensors = set(header) - {"__metadata__"}
    if not tensors:
        raise ValueError("No tensor entries in safetensors header")
    for name in tensors:
        item = header[name]
        if not isinstance(item, dict):
            raise ValueError("Invalid safetensors tensor entry")
        shape, offsets = item.get("shape"), item.get("data_offsets")
        if (not isinstance(shape, list) or any(type(n) is not int or n < 0 for n in shape)
                or not isinstance(item.get("dtype"), str)
                or not isinstance(offsets, list) or len(offsets) != 2
                or any(type(n) is not int for n in offsets)
                or not 0 <= offsets[0] <= offsets[1] <= size - 8 - length):
            raise ValueError("Invalid tensor shape/dtype/offsets in safetensors header")
    return tensors, {"file": path.name, "file_bytes": size, "header_bytes": length + 8,
                     "header_sha256": hashlib.sha256(prefix + raw).hexdigest()}


def inspect_model(root):
    config = read_json(root / "config.json")
    read_json(root / "tokenizer_config.json")
    alternatives = (("tokenizer.json",), ("tokenizer.model",), ("vocab.json", "merges.txt"))
    readable_tokenizer = False
    for names in alternatives:
        try:
            for name in names:
                with (root / name).open("rb") as stream:
                    if not stream.read(1):
                        raise ValueError("Empty tokenizer payload")
            readable_tokenizer = True
            break
        except (OSError, ValueError):
            continue
    if not readable_tokenizer:
        raise ValueError("No readable nonempty tokenizer payload found")
    index_path = root / "model.safetensors.index.json"
    weight_map = None
    if index_path.is_file():
        weight_map = read_json(index_path).get("weight_map")
        if not isinstance(weight_map, dict) or not weight_map:
            raise ValueError("Safetensors index has no weight_map")
        if any(not isinstance(k, str) or not isinstance(v, str) for k, v in weight_map.items()):
            raise ValueError("Invalid weight_map entries")
        names = sorted(set(weight_map.values()))
    else:
        names = sorted(p.name for p in root.glob("*.safetensors"))
    if not names:
        raise ValueError("No local safetensors shards found")
    shards, seen = [], set()
    for name in names:
        relative = PurePosixPath(name)
        if (relative.is_absolute() or "\\" in name or ":" in name
                or any(p in ("", ".", "..") for p in name.split("/"))
                or relative.suffix != ".safetensors"):
            raise ValueError("Unsafe/non-safetensors shard reference")
        tensors, header = inspect_header(root.joinpath(*relative.parts))
        if seen.intersection(tensors):
            raise ValueError("Duplicate tensors across shards")
        if weight_map is not None and any(weight_map.get(t) != name for t in tensors):
            raise ValueError("Shard headers disagree with weight_map")
        seen.update(tensors)
        header["file"] = name
        shards.append(header)
    if weight_map is not None and set(weight_map) != seen:
        raise ValueError("Index references missing tensor headers")
    return {"path": str(root), "shards": shards, "model_type": config.get("model_type"),
            "validation": "config/tokenizer presence and bounded safetensors headers only",
            "tensor_payload_read": False, "full_weight_hash_verified": False}


def child_environment(root):
    env = os.environ.copy()
    for name in ("OPENAI_API_KEY", "VLLM_API_KEY", "TRIAL_VLLM_API_KEY"):
        env.pop(name, None)
    env.update(PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1",
               HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1",
               VLLM_NO_USAGE_STATS="1", DO_NOT_TRACK="1", TOKENIZERS_PARALLELISM="false",
               SHORE_TEST_ROOT=str(root), RIFT_PUBLIC_ROOT=str(root))
    return env


def run_command(report, name, category, command, root, timeout, structured=False):
    try:
        result = subprocess.run(command, cwd=root, env=child_environment(root),
                                capture_output=True, text=True, timeout=timeout, check=False)
        details = {"returncode": result.returncode}
        if structured:
            lines = [line[len(MARKER):] for line in result.stdout.splitlines() if line.startswith(MARKER)]
            if len(lines) != 1:
                raise ValueError("Child did not return exactly one structured probe record")
            probe = parse_json(lines[0])
            if not isinstance(probe, dict) or type(probe.get("ok")) is not bool:
                raise ValueError("Invalid structured probe record")
            details["probe"] = probe
            passed = result.returncode == 0 and probe["ok"]
            if passed:
                if probe.get("python", [])[:2] != [3, 12]:
                    raise ValueError("Probe lacks verified Python 3.12 evidence")
                if name == "trial_imports":
                    if (probe.get("numpy") != "2.1.3" or probe.get("scipy") != "1.15.3"
                            or not probe.get("rift_numerics_origin")
                            or Path(probe["rift_numerics_origin"]).resolve()
                            != (root / "rift_numerics/__init__.py").resolve()
                            or probe.get("rift_numerics_executed") is not False):
                        raise ValueError("Probe lacks trial dependency evidence")
                elif name == "gpu_runtime":
                    devices = probe.get("devices", [])
                    if (probe.get("vllm", "").split("+")[0] != "0.32.0"
                            or probe.get("cuda_runtime") != "12.9" or not probe.get("torch")
                            or not probe.get("torch_distribution")
                            or set(probe.get("imported_extensions", [])) != {
                                "vllm._C_stable_libtorch", "vllm._moe_C_stable_libtorch"}
                            or probe.get("visible_device_count") != 4 or len(devices) != 4
                            or any(not isinstance(d, dict) or d.get("index") != i
                                   or d.get("bf16_ok") is not True
                                   or d.get("compute_capability") != [8, 9]
                                   or "4090" not in d.get("name", "")
                                   or d.get("total_memory_bytes", 0) < 40 * 2**30 for i, d in enumerate(devices))):
                        raise ValueError("Probe lacks four-card SM8.9/BF16/dependency evidence")
            if not passed:
                category = probe.get("category", category)
        else:
            passed = result.returncode == 0 and "usage:" in result.stdout.lower()
        if not passed:
            details["stderr_tail"] = result.stderr[-4000:]
            if not structured:
                details["stdout_tail"] = result.stdout[-4000:]
        record(report, name, "pass" if passed else "fail", category, **details)
        return passed
    except subprocess.TimeoutExpired:
        record(report, name, "fail", category, error=f"Probe timed out after {timeout}s; no scientific score produced")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        record(report, name, "fail", category, error=f"{type(exc).__name__}: {exc}")
    return False


def record_driver_inventory(report, root, timeout):
    """Diagnostic inventory only; successful real CUDA tests decide compatibility.

    The scheduler may expose fewer GPUs to CUDA than nvidia-smi lists. Never
    replace CUDA_VISIBLE_DEVICES or impose a guessed minimum driver version.
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,driver_version,memory.total", "--format=csv,noheader,nounits"],
            cwd=root, env=child_environment(root), capture_output=True, text=True,
            timeout=timeout, check=False)
        if result.returncode:
            raise ValueError(f"nvidia-smi exited {result.returncode}: {result.stderr[-2000:]}")
        inventory = []
        for row in csv.reader(io.StringIO(result.stdout)):
            if not row:
                continue
            if len(row) != 4:
                raise ValueError("Unexpected nvidia-smi inventory fields")
            index, name, driver, mib = (item.strip() for item in row)
            if not driver or not name or not math.isfinite(float(mib)) or float(mib) <= 0:
                raise ValueError("Incomplete nvidia-smi inventory record")
            inventory.append(dict(index=index, name=name, driver_version=driver, memory_total_mib=float(mib)))
        if not inventory:
            raise ValueError("Empty nvidia-smi inventory")
        record(report, "driver_inventory", "pass", "driver_runtime", inventory=inventory,
               note="Diagnostic inventory; allocated visible devices and real CUDA compatibility are checked by torch.")
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        record(report, "driver_inventory", "warning", "driver_runtime", error=f"{type(exc).__name__}: {exc}",
               note="Inventory unavailable; four-card CUDA/BF16 probe remains mandatory.")


def build_report(root, model_root, phase="installed", timeout=180):
    report = {"schema_version": "1.0.0", "created_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "private_4090_environment_only", "phase": phase, "test_root": str(root),
              "model_root": str(model_root), "status": "blocked", "checks": [],
              "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
              "network_check": "not_tested; offline probes only; installation downloads are a separate step",
              "model_or_api_or_physics_calls": 0, "scientific_score": None,
              "limitations": ["No LLM loading, prefill, generation, FP8 MoE or TP4 service checks performed.",
                              "No nine-world calibration or scientific acceptance performed.",
                              "Infrastructure failures must not be treated as a zero scientific score.",
                              "No installation, downloads, driver changes or environment deletion performed."]}
    valid_bundle = attempt(report, "extracted_bundle", "filesystem", lambda: inspect_bundle(root))
    if valid_bundle:
        attempt(report, "output_and_cache_writability", "filesystem", lambda: inspect_writable(root))
    for name in MODEL_NAMES:
        attempt(report, f"model_files:{name}", "model_files", lambda name=name: inspect_model(model_root / name))
    pythons = {"trial": root / ".venv-trial/bin/python", "vllm": root / ".venv-vllm/bin/python"}
    for role, python in pythons.items():
        exists = python.is_file() and os.access(python, os.X_OK)
        record(report, f"{role}_python_path", "pass" if exists else ("not_installed" if phase == "paths" else "fail"),
               "installation", path=str(python), runtime_version_verified=False,
               note="The installed phase verifies Python 3.12; base Python is not used for probes.")
    if phase == "installed" and not any(c["status"] == "fail" for c in report["checks"]):
        cpu_ok = run_command(report, "trial_imports", "installation",
                             [str(pythons["trial"]), "-c", CPU_PROBE, str(root)], root, timeout, structured=True)
        if cpu_ok:
            run_command(report, "calibration_cli_help", "installation",
                        [str(pythons["trial"]), "-c", HELP_PROBE,
                         str(root / "open_model_calibration.py"), "--help"], root, timeout)
        record_driver_inventory(report, root, timeout)
        run_command(report, "gpu_runtime", "driver_runtime",
                    [str(pythons["vllm"]), "-c", GPU_PROBE], root, timeout, structured=True)
    elif phase == "installed":
        record(report, "installed_probes", "skipped", "installation",
               reason="Required paths/files are unavailable; no environment subprocess was started.")
    if not any(c["status"] == "fail" for c in report["checks"]):
        report["status"] = "paths_checked" if phase == "paths" else "ready_for_model_service_checks"
    return report


def save_new_report(path, report):
    """Write a new private report; never overwrite an earlier run."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        # This is only the new partial report created by this call.
        path.unlink(missing_ok=True)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    parser.add_argument("--phase", choices=("paths", "installed"), default="installed")
    parser.add_argument("--plan", "--check-only", dest="paths_only", action="store_true",
                        help="Path/header checks only; no subprocess, GPU or network calls")
    parser.add_argument("--report", type=Path, help="New JSON report; existing files are never overwritten")
    parser.add_argument("--timeout", type=float, default=180, help="Per-subprocess timeout in seconds")
    args = parser.parse_args(argv)
    if not 0 < args.timeout <= 3600:
        parser.error("--timeout must be positive and no more than 3600 seconds")
    root, model_root = args.test_root.resolve(), args.model_root.resolve()
    phase = "paths" if args.paths_only else args.phase
    report = build_report(root, model_root, phase, args.timeout)
    target = args.report.resolve() if args.report else root / "checks" / (
        "environment-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + ".json")
    report["report_path"] = str(target)
    record(report, "report_write", "pass", "report_io", path=str(target))
    try:
        if not args.report and not root.is_dir():
            raise ValueError("Missing test-root; refusing to create a fake extraction directory for the report")
        save_new_report(target, report)
    except (OSError, ValueError, TypeError) as exc:
        report["checks"][-1].update(status="fail", error=f"{type(exc).__name__}: {exc}")
        report["status"] = "blocked"
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    print(f"{report['status']}: {target}\nModel service and nine-world calibration remain unverified.", file=sys.stderr)
    return 2 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
