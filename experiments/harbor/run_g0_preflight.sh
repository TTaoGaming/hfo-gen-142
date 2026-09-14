#!/usr/bin/env bash
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"
INDEX_DIR="${HARBOR_INDEX_DIR:-/var/lib/hfo-desktop-commander/bench/harbor-index}"
cd "$INDEX_DIR"

command -v harbor >/dev/null
harbor --version

# Zero-spend hosted preflight. This intentionally uses oracle so no model
# credential is needed merely to validate the benchmark/job shape.
harbor run \
  -c job-config.yaml \
  -a oracle \
  -d harbor-index/harbor-index@latest \
  --n-attempts 1 \
  --n-tasks 1 \
  --launch \
  --dry-run \
  --no-secrets \
  --yes
