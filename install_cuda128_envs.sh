#!/usr/bin/env bash
# Compatibility launcher; the sibling canonical bootstrap owns all installation.
# Python packages default to the supplied mirror only; upstream fallback requires
# an explicit --allow-official-fallback. Existing environments/downloads are kept.
set -euo pipefail

SCRIPT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
arguments=()
while [ "$#" -gt 0 ]; do
    case "$1" in
        --test-root)
            [ "$#" -ge 2 ] || { printf '%s\n' '--test-root requires a path' >&2; exit 2; }
            arguments+=(--env-root "$2")
            shift 2
            ;;
        *) arguments+=("$1"); shift ;;
    esac
done
for name in bootstrap_cuda128.sh pip_index_install.py prepare_vllm_dependencies.py preflight_cuda128_build.py prepare_torch_wheel.py; do
    [ -f "$SCRIPT_ROOT/$name" ] || {
        printf 'Missing matching installer component: %s\n' "$SCRIPT_ROOT/$name" >&2
        exit 2
    }
done
exec bash "$SCRIPT_ROOT/bootstrap_cuda128.sh" "${arguments[@]}"
