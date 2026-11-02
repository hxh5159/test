#!/usr/bin/env bash
# Separate CUDA 12.8 source-build profile; preserves the earlier cu129 environments.
set -euo pipefail
umask 077

SCRIPT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
TEST_ROOT="$(dirname -- "$SCRIPT_ROOT")/shore-organizer-4090-test-20261101"
INDEX_URL=''
TRUSTED_HOST=''
PLAN=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --test-root) TEST_ROOT="${2:?Missing test root}"; shift 2 ;;
        --index-url) INDEX_URL="${2:?Missing package index}"; shift 2 ;;
        --trusted-host) TRUSTED_HOST="${2:?Missing trusted host}"; shift 2 ;;
        --plan) PLAN=1; shift ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
    esac
done
die() { printf '%s\n' "$*" >&2; exit 2; }
[ -n "$TEST_ROOT" ] && [ "$TEST_ROOT" != / ] && [ -d "$TEST_ROOT" ] || die 'An existing extracted --test-root is required.'
TEST_ROOT="$(cd -- "$TEST_ROOT" && pwd -P)"
[ "$TEST_ROOT" != / ] || die 'The filesystem root is not a test directory.'
for name in env_open_models.sh requirements-trials.txt open_model_calibration.py; do
    [ -f "$TEST_ROOT/$name" ] || die "Missing bundle file: $TEST_ROOT/$name"
done
TRIAL_ENV="$TEST_ROOT/.venv-trial"
MODEL_ENV="$TEST_ROOT/.venv-vllm-cu128"
if [ "$PLAN" -eq 1 ]; then
    printf 'Trial: %s\nNew model environment: %s\nVersions: Python 3.12, torch 2.11.0+cu128, vLLM 0.24.0 source, transformers 5.8.0\nNo installation, network, GPU or model calls performed.\n' "$TRIAL_ENV" "$MODEL_ENV"
    exit 0
fi
[ -n "$INDEX_URL" ] && [ -n "$TRUSTED_HOST" ] || die '--index-url and --trusted-host are required.'
export PATH="$HOME/.local/bin:$PATH"
for executable in uv git gcc g++; do
    command -v "$executable" >/dev/null || die "Missing build tool: $executable"
done
CUDA_ROOT="${SHORE_CUDA128_HOME:-${CUDA_HOME:-}}"
if [ -z "$CUDA_ROOT" ]; then
    if [ -x /usr/local/cuda-12.8/bin/nvcc ]; then
        CUDA_ROOT=/usr/local/cuda-12.8
    elif command -v nvcc >/dev/null; then
        CUDA_ROOT="$(dirname -- "$(dirname -- "$(readlink -f -- "$(command -v nvcc)")")")"
    fi
fi
[ -n "$CUDA_ROOT" ] && [ -x "$CUDA_ROOT/bin/nvcc" ] || die 'CUDA Toolkit 12.8 nvcc is missing. nvidia-smi does not verify the Toolkit. Set SHORE_CUDA128_HOME to its installed directory.'
"$CUDA_ROOT/bin/nvcc" --version | grep -Eq 'release 12\.8([,[:space:]]|$)' || die 'Expected nvcc release 12.8.'
GCC_VERSION="$(gcc -dumpfullversion -dumpversion)"
GXX_VERSION="$(g++ -dumpfullversion -dumpversion)"
for version in "$GCC_VERSION" "$GXX_VERSION"; do
    minimum="$(printf '%s\n' 11.3 "$version" | sort -V | head -n 1)"
    [ "$minimum" = 11.3 ] || die "GCC and G++ >=11.3 are required; found $GCC_VERSION / $GXX_VERSION."
    [ "${version%%.*}" -le 14 ] || die 'Use GCC/G++ 11.3 through 14 for this CUDA 12.8 profile.'
done
export CUDA_HOME="$CUDA_ROOT"
export PATH="$CUDA_HOME/bin:$PATH"
export CC="$(command -v gcc)"
export CXX="$(command -v g++)"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export MAX_JOBS="${SHORE_BUILD_JOBS:-4}"
export NVCC_THREADS=1
export VLLM_TARGET_DEVICE=cuda
export VLLM_USE_PRECOMPILED=0
export VLLM_USE_PRECOMPILED_RUST=0
export VLLM_USE_RUST_FRONTEND=0
export VLLM_REQUIRE_RUST_FRONTEND=0

for location in "$TRIAL_ENV" "$MODEL_ENV"; do
    if [ ! -x "$location/bin/python" ]; then
        [ ! -e "$location" ] || die "Incomplete environment preserved; inspect it before retrying: $location"
        uv venv --python 3.12 "$location"
    fi
    "$location/bin/python" -c 'import sys; assert sys.version_info[:2] == (3, 12), "Python 3.12 is required"'
    "$location/bin/python" -m ensurepip --upgrade
done
pip_install() {
    local interpreter="$1"
    shift
    env -u PIP_EXTRA_INDEX_URL -u PIP_INDEX_URL \
        PIP_CONFIG_FILE=/dev/null \
        "$interpreter" -m pip install "$@" \
        --index-url "$INDEX_URL" --trusted-host "$TRUSTED_HOST" \
        --no-cache-dir --timeout 600 --retries 5
}
pip_install "$TRIAL_ENV/bin/python" -r "$TEST_ROOT/requirements-trials.txt"
pip_install "$MODEL_ENV/bin/python" --upgrade pip
pip_install "$MODEL_ENV/bin/python" \
    --find-links https://download.pytorch.org/whl/cu128/torch/ \
    --find-links https://download.pytorch.org/whl/cu128/torchvision/ \
    --find-links https://download.pytorch.org/whl/cu128/torchaudio/ \
    'torch==2.11.0+cu128' 'torchvision==0.26.0+cu128' 'torchaudio==2.11.0+cu128'
"$MODEL_ENV/bin/python" - <<'PY'
import torch
assert torch.version.cuda == '12.8', torch.version.cuda
assert torch.cuda.is_available(), 'CUDA initialization failed'
assert torch.cuda.device_count() > 0, 'No allocated visible GPU'
for i in range(torch.cuda.device_count()):
    with torch.cuda.device(i):
        x = torch.ones((128, 128), device=f'cuda:{i}', dtype=torch.bfloat16)
        assert (x @ x)[0, 0].item() == 128
        torch.cuda.synchronize()
        print('BF16 check passed:', i, torch.cuda.get_device_name(i))
PY
export TORCH_CUDA_ARCH_LIST
TORCH_CUDA_ARCH_LIST="$("$MODEL_ENV/bin/python" -c 'import torch; print(";".join(sorted({"%d.%d" % torch.cuda.get_device_capability(i) for i in range(torch.cuda.device_count())})))')"
BUILD_ROOT="$(mktemp -d "$TEST_ROOT/build-vllm-cu128.XXXXXXXX")"
git clone --depth 1 --branch v0.24.0 https://github.com/vllm-project/vllm.git "$BUILD_ROOT/source"
CONSTRAINTS="$BUILD_ROOT/constraints-cu128.txt"
printf '%s\n' 'torch==2.11.0+cu128' 'torchvision==0.26.0+cu128' 'torchaudio==2.11.0+cu128' 'transformers==5.8.0' > "$CONSTRAINTS"
pip_install "$MODEL_ENV/bin/python" -c "$CONSTRAINTS" -r "$BUILD_ROOT/source/requirements/build/cuda.txt"
# setup.py selects CUDA 12 dependency variants from the installed torch build.
pip_install "$MODEL_ENV/bin/python" -c "$CONSTRAINTS" --no-build-isolation \
    "$BUILD_ROOT/source" 'transformers==5.8.0'
"$MODEL_ENV/bin/python" -m pip check
(cd "$TEST_ROOT" && "$MODEL_ENV/bin/python" - <<'PY'
import importlib.metadata as md
import torch
import vllm._C_stable_libtorch
import vllm._moe_C_stable_libtorch
assert torch.version.cuda == '12.8'
assert md.version('vllm').split('+')[0] == '0.24.0', md.version('vllm')
assert md.version('transformers') == '5.8.0'
print('Installed:', {name: md.version(name) for name in ('torch', 'vllm', 'transformers')})
print('Torch CUDA runtime:', torch.version.cuda)
PY
)
"$MODEL_ENV/bin/vllm" serve --help > "$BUILD_ROOT/serve-help.txt"
printf '\nInstallation and basic CUDA/import checks passed.\nActivate: source %q/bin/activate\nUse this environment\x27s vllm serve directly. The previous serve_open_models.py and check_4090_environment.py remain tied to 0.32/cu129.\nFull model loading, FP8 kernels and competition runs are not validated by this installer.\n' "$MODEL_ENV"
