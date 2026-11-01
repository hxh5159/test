#!/usr/bin/env bash
# Organizer-only environment recovery. No model loading or science evaluation.
set -euo pipefail
umask 077

SCRIPT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
INSTALL_ROOT="$(dirname -- "$SCRIPT_ROOT")/shore-organizer-4090-test-20261101"
PLAN_ONLY=0
CACHE_OVERRIDE="${SHORE_INSTALL_CACHE_DIR:-}"
while [ "$#" -gt 0 ]; do
    case "$1" in
        --test-root) [ "$#" -ge 2 ] || { printf 'Missing --test-root value\n' >&2; exit 2; }; INSTALL_ROOT="$2"; shift 2 ;;
        --plan) PLAN_ONLY=1; shift ;;
        --cache-dir) [ "$#" -ge 2 ] && [ -n "$2" ] || { printf 'Missing --cache-dir value\n' >&2; exit 2; }; CACHE_OVERRIDE="$2"; shift 2 ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
    esac
done
if [ "$CACHE_OVERRIDE" = / ]; then
    printf 'Stop: --cache-dir must not be the filesystem root.\n' >&2
    exit 2
fi

if [ -z "$INSTALL_ROOT" ] || [ "$INSTALL_ROOT" = / ] || [ ! -d "$INSTALL_ROOT" ]; then
    printf 'Stop: --test-root must be an existing extracted private bundle directory.\n' >&2
    exit 2
fi
INSTALL_ROOT="$(cd -- "$INSTALL_ROOT" && pwd -P)"
if [ "$INSTALL_ROOT" = / ]; then
    printf 'Stop: resolved --test-root must not be the filesystem root.\n' >&2
    exit 2
fi
for required in env_open_models.sh requirements-trials.txt open_model_calibration.py; do
    if [ ! -f "$INSTALL_ROOT/$required" ]; then
        printf 'Stop: required bundle file missing: %s/%s\n' "$INSTALL_ROOT" "$required" >&2
        exit 2
    fi
done
if [ "$PLAN_ONLY" -eq 1 ]; then
    printf 'Trial environment: %s/.venv-trial\nvLLM environment: %s/.venv-vllm\nNo installation or GPU calls performed.\n' "$INSTALL_ROOT" "$INSTALL_ROOT"
    exit 0
fi

export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
    printf 'Stop: uv is not installed. Install uv first; this script does not modify the base Python.\n' >&2
    exit 2
fi
# Preserve downloads from the failed attempt before env_open_models resets caches.
INSTALL_CACHE="${CACHE_OVERRIDE:-$(uv cache dir)}"
if [ -d "$INSTALL_CACHE" ]; then
    INSTALL_CACHE="$(cd -- "$INSTALL_CACHE" && pwd -P)"
    if [ "$INSTALL_CACHE" = / ]; then
        printf 'Stop: resolved cache directory must not be the filesystem root.\n' >&2
        exit 2
    fi
fi
source "$INSTALL_ROOT/env_open_models.sh"
if [ "${SHORE_TEST_ROOT:-}" != "$INSTALL_ROOT" ]; then
    printf 'Stop: sourced SHORE_TEST_ROOT differs from the checked bundle directory.\n' >&2
    exit 2
fi
export UV_CACHE_DIR="$INSTALL_CACHE"
export UV_HTTP_TIMEOUT="${SHORE_INSTALL_HTTP_TIMEOUT:-600}"
export UV_HTTP_RETRIES=5
export UV_CONCURRENT_DOWNLOADS="${SHORE_INSTALL_CONCURRENCY:-2}"
export UV_LINK_MODE=copy
printf 'Using existing uv cache: %s\nHTTP read timeout: %ss; concurrent downloads: %s\n' "$UV_CACHE_DIR" "$UV_HTTP_TIMEOUT" "$UV_CONCURRENT_DOWNLOADS"

for name in .venv-trial .venv-vllm; do
    location="$INSTALL_ROOT/$name"
    if [ ! -x "$location/bin/python" ]; then
        if [ -e "$location" ]; then
            printf 'Stop: incomplete environment exists at %s; preserve it and inspect before replacing.\n' "$location" >&2
            exit 2
        fi
        uv venv --python 3.12 "$location"
    fi
    "$location/bin/python" -c 'import sys; assert sys.version_info[:2] == (3, 12), "Expected Python 3.12"'
done

uv pip install --python "$INSTALL_ROOT/.venv-trial/bin/python" \
    --default-index https://pypi.org/simple -r "$INSTALL_ROOT/requirements-trials.txt"
uv pip install --python "$INSTALL_ROOT/.venv-vllm/bin/python" \
    --default-index https://pypi.org/simple --torch-backend=cu129 \
    'https://github.com/vllm-project/vllm/releases/download/v0.32.0/vllm-0.32.0%2Bcu129-cp38-abi3-manylinux_2_28_x86_64.whl#sha256=9918be806fb2808c406547ff4f9f43870ac6ff28dc4b179291fcf532145bb50b'

"$INSTALL_ROOT/.venv-vllm/bin/python" - <<'PY'
import importlib.metadata as md
import sys
import torch
import vllm._C_stable_libtorch
import vllm._moe_C_stable_libtorch
print('Python:', sys.executable)
print('vLLM:', md.version('vllm'), 'Torch:', torch.__version__, 'CUDA runtime:', torch.version.cuda)
assert (torch.version.cuda or '').startswith('12.9'), 'Expected the matching cu129 Torch build'
assert torch.cuda.is_available(), 'CUDA initialization failed; inspect the actual error before changing drivers'
assert torch.cuda.device_count() == 4, 'Expected exactly the four allocated visible GPUs'
for i in range(4):
    with torch.cuda.device(i):
        x = torch.ones((128, 128), device=f'cuda:{i}', dtype=torch.bfloat16)
        result = x @ x
        torch.cuda.synchronize(i)
        assert float(result[0, 0]) == 128.
        print('Basic BF16 computation passed:', i, torch.cuda.get_device_name(i))
print('Basic checks passed. Full vLLM prefill, generation and FP8 MoE kernels still require model-service smoke tests.')
PY
"$INSTALL_ROOT/.venv-vllm/bin/python" -m vllm.entrypoints.cli.main --version
"$INSTALL_ROOT/.venv-vllm/bin/python" -m vllm.entrypoints.cli.main download-kernels
printf '\nEnvironment setup completed. Activate using:\nsource %q/.venv-vllm/bin/activate\n' "$INSTALL_ROOT"
