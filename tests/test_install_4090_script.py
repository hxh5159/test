"""Run the complete installer control flow with fake uv/Python, never install."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = ("C:/Program Files/Git/bin/bash.exe" if Path("C:/Program Files/Git/bin/bash.exe").is_file()
        else shutil.which("bash"))


@unittest.skipUnless(BASH, "Bash unavailable")
class InstallerFlowTests(unittest.TestCase):
    def setUp(self):
        (ROOT/"checks").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT/"checks", prefix="mock-install-")
        self.base = Path(self.temp.name)
        self.bundle = self.base/"private bundle"
        self.bundle.mkdir()
        (self.bundle/"env_open_models.sh").write_text(
            'export SHORE_TEST_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"\n'
            'export UV_CACHE_DIR="$SHORE_TEST_ROOT/new-empty-cache"\n', newline="\n")
        (self.bundle/"requirements-trials.txt").write_text("synthetic only\n")
        (self.bundle/"open_model_calibration.py").write_text("# not executed\n")
        self.calls = self.base/"calls.log"
        self.python = self.base/"fake-python.sh"
        self.python.write_text('''#!/usr/bin/env bash
set -eu
printf 'PY %s\\n' "$*" >> "$SHORE_FAKE_CALLS"
if [ "${1:-}" = - ]; then
    cat >> "$SHORE_FAKE_CALLS"
fi
exit 0
''', newline="\n")
        self.uv = self.base/"fake-uv.sh"
        self.uv.write_text('''#!/usr/bin/env bash
set -eu
printf 'UV %s CACHE=%s\\n' "$*" "${UV_CACHE_DIR:-unset}" >> "$SHORE_FAKE_CALLS"
case "${1:-}" in
  cache) printf '%s\\n' "$SHORE_FAKE_DEFAULT_CACHE" ;;
  venv)
    target="${@: -1}"
    mkdir -p "$target/bin"
    cp "$SHORE_FAKE_PYTHON" "$target/bin/python"
    chmod +x "$target/bin/python"
    ;;
  pip) if [ "${SHORE_FAKE_FAIL_PIP:-0}" = 1 ]; then exit 17; fi ;;
  *) exit 99 ;;
esac
''', newline="\n")
        self.python.chmod(0o700)
        self.uv.chmod(0o700)

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, *args, fail_pip=False):
        env = os.environ.copy()
        env.update(SHORE_FAKE_UV=self.uv.as_posix(), SHORE_FAKE_PYTHON=self.python.as_posix(),
            SHORE_FAKE_CALLS=self.calls.as_posix(), SHORE_FAKE_DEFAULT_CACHE=(self.base/"previous-cache").as_posix(),
            SHORE_FAKE_FAIL_PIP="1" if fail_pip else "0", SHORE_TEST_ROOT="")
        script = 'uv() { bash "$SHORE_FAKE_UV" "$@"; }; export -f uv; bash "$@"'
        return subprocess.run([BASH, "-c", script, "mock-bootstrap",
            (ROOT/"install_4090_envs.sh").as_posix(), *args], capture_output=True, text=True, encoding="utf-8", env=env)

    def test_full_mock_flow_uses_checked_paths_and_correct_extensions(self):
        old_cache = self.base/"cached downloads"
        old_cache.mkdir()
        result = self.invoke("--test-root", self.bundle.as_posix(), "--cache-dir", old_cache.as_posix())
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        calls = self.calls.read_text()
        self.assertIn("Environment setup completed", result.stdout)
        self.assertIn("cached downloads", calls)
        self.assertIn("/.venv-trial/bin/python", calls)
        self.assertIn("/.venv-vllm/bin/python", calls)
        self.assertNotIn("--python /.venv-", calls)
        self.assertIn("import vllm._C_stable_libtorch", calls)
        self.assertIn("import vllm._moe_C_stable_libtorch", calls)
        self.assertNotIn("import vllm._C\n", calls)
        self.assertIn("download-kernels", calls)
        self.assertIn("--torch-backend=cu129", calls)

    def test_download_failure_stops_before_cuda_or_kernel_pretend_checks(self):
        result = self.invoke("--test-root", self.bundle.as_posix(), fail_pip=True)
        self.assertEqual(result.returncode, 17, result.stdout+result.stderr)
        calls = self.calls.read_text()
        self.assertNotIn("import torch", calls)
        self.assertNotIn("download-kernels", calls)
        self.assertNotIn("Environment setup completed", result.stdout)

    def test_plan_and_missing_path_never_invoke_uv(self):
        for args, code in [(("--plan", "--test-root", self.bundle.as_posix()), 0),
                           (("--plan", "--test-root", ""), 2),
                           (("--plan", "--test-root", "/"), 2),
                           (("--plan", "--test-root", self.bundle.as_posix(), "--cache-dir", "/"), 2)]:
            result = self.invoke(*args)
            self.assertEqual(result.returncode, code, result.stdout+result.stderr)
        self.assertFalse(self.calls.exists())

    def test_repeat_mock_install_preserves_existing_environments_and_results(self):
        arguments = ("--test-root", self.bundle.as_posix())
        self.assertEqual(self.invoke(*arguments).returncode, 0)
        result_file = self.bundle/"results"/"keep.txt"
        result_file.parent.mkdir()
        result_file.write_text("preserve")
        before = self.calls.read_text().count("UV venv")
        self.assertEqual(self.invoke(*arguments).returncode, 0)
        self.assertEqual(self.calls.read_text().count("UV venv"), before)
        self.assertEqual(result_file.read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
