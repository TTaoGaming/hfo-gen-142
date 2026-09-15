#!/usr/bin/env bash
set -euo pipefail

# Rootless installer only. This does not create a daemon, scheduler, queue, lease,
# service, or semantic state owner. It installs bounded policy/admission/execution gates.
REPO_URL="https://github.com/TTaoGaming/hfo-gen-142.git"
ROOT="${HFO_GEN142_ROOT:-$HOME/.local/share/hfo-gen-142}"
BIN="$HOME/.local/bin"
STATE="$HOME/.local/state/hfo-gen142-forcing"
REV="${HFO_GEN142_REF:-}"

hold() { echo "HOLD: $1" >&2; exit 22; }
[[ "$REV" =~ ^[0-9a-f]{40}$ && "$REV" != 0000000000000000000000000000000000000000 ]] || hold 'immutable HFO_GEN142_REF required'

command -v python3 >/dev/null || { echo 'HOLD: python3 missing' >&2; exit 20; }
command -v git >/dev/null || { echo 'HOLD: git missing' >&2; exit 21; }
export PYTHONDONTWRITEBYTECODE=1
SOURCE="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
[[ "$(git -C "$SOURCE" rev-parse HEAD)" == "$REV" ]] || hold 'installer source revision mismatch'
[[ -z "$(git -C "$SOURCE" status --porcelain --untracked-files=all)" ]] || hold 'installer source dirty'
# Reject incomplete revisions before an existing installed checkout can move.
for entry in tools/holon_gate.py ops/vps_exec_guard.py tools/reconcile_kernel.py tools/janitor_gate.py ops/janitor_exec.py; do
  [[ "$(git -C "$SOURCE" ls-tree "$REV" -- "$entry")" == "100755 blob "* ]] || hold 'source entry point is not an executable blob'
done

check_destination() {
  [[ ! -L "$ROOT" ]] || hold 'destination symlink refused'
  if [[ -e "$ROOT" ]]; then
    [[ -d "$ROOT/.git" ]] || hold 'existing destination is not a standalone checkout'
    [[ "$(git -C "$ROOT" remote get-url origin)" == "$REPO_URL" ]] || hold 'destination origin mismatch'
    [[ -z "$(git -C "$ROOT" status --porcelain --untracked-files=all)" ]] || hold 'destination dirty'
  fi
}
check_destination

# Validate the immutable source before changing the installed checkout or tools.
# Do not generate untracked bytecode that would invalidate the next clean check.
(
  cd "$SOURCE"
  python3 -B -m unittest discover -s tests -p 'test_holon_gate.py'
  python3 -B -m unittest discover -s tests -p 'test_reconcile_kernel.py'
  python3 -B -m unittest discover -s tests -p 'test_janitor_gate.py'
)
[[ "$(git -C "$SOURCE" rev-parse HEAD)" == "$REV" ]] || hold 'installer source moved during verification'
[[ -z "$(git -C "$SOURCE" status --porcelain --untracked-files=all)" ]] || hold 'installer source changed during verification'
check_destination

mkdir -p "$BIN" "$STATE" "$(dirname "$ROOT")"
if [[ ! -e "$ROOT" ]]; then
  git init --quiet "$ROOT"
  git -C "$ROOT" remote add origin "$REPO_URL"
fi
git -C "$ROOT" fetch --quiet --no-tags --depth 1 origin "$REV"
[[ "$(git -C "$ROOT" rev-parse FETCH_HEAD)" == "$REV" ]] || hold 'fetched revision mismatch'
git -C "$ROOT" checkout --quiet --detach "$REV"
[[ "$(git -C "$ROOT" rev-parse HEAD)" == "$REV" ]] || hold 'installed revision mismatch'
check_destination

# These entry points are executable in the admitted Git revision. Changing file
# modes after checkout would make later installations correctly refuse as dirty.
for entry in tools/holon_gate.py ops/vps_exec_guard.py tools/reconcile_kernel.py tools/janitor_gate.py ops/janitor_exec.py; do
  [[ -x "$ROOT/$entry" ]] || hold 'installed entry point is not executable'
done

ln -sfn "$ROOT/tools/holon_gate.py" "$BIN/hfo-holon-gate"
ln -sfn "$ROOT/ops/vps_exec_guard.py" "$BIN/hfo-vps-exec"
ln -sfn "$ROOT/tools/reconcile_kernel.py" "$BIN/hfo-reconcile"
ln -sfn "$ROOT/tools/janitor_gate.py" "$BIN/hfo-janitor-gate"
ln -sfn "$ROOT/ops/janitor_exec.py" "$BIN/hfo-janitor-exec"
commit="$(git -C "$ROOT" rev-parse HEAD)"
python3 -B - "$STATE/install.json" "$commit" "$REV" <<'PY'
import json, os, platform, sys
from datetime import datetime, timezone
from pathlib import Path
p=Path(sys.argv[1])
pending=p.with_suffix('.pending')
pending.write_text(json.dumps({
  'schema':'hfo.forcing-install.v1',
  'observed_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
  'repo_commit':sys.argv[2],
  'requested_commit':sys.argv[3],
  'platform':{'system':platform.system(),'machine':platform.machine()},
  'semantic_owner':'hfo-sigrun-va-r0',
  'note':'rootless gates only; no scheduler/queue/lease/state owner installed'
},sort_keys=True)+'\n',encoding='utf-8')
os.replace(pending,p)
PY

echo "ADMIT: installed holon + reconcile + janitor gates/executors at commit $commit"
echo "No service or scheduler was created. Existing Sigrun DO remains semantic owner."
