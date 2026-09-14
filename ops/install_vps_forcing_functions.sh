#!/usr/bin/env bash
set -euo pipefail

# Rootless installer only. This does not create a daemon, scheduler, queue, lease,
# service, or semantic state owner. It installs two admission/execution gates.
REPO_URL="https://github.com/TTaoGaming/hfo-gen-142.git"
ROOT="${HFO_GEN142_ROOT:-$HOME/.local/share/hfo-gen-142}"
BIN="$HOME/.local/bin"
STATE="$HOME/.local/state/hfo-gen142-forcing"

command -v python3 >/dev/null || { echo 'HOLD: python3 missing' >&2; exit 20; }
command -v git >/dev/null || { echo 'HOLD: git missing' >&2; exit 21; }
mkdir -p "$BIN" "$STATE" "$(dirname "$ROOT")"

if [[ -d "$ROOT/.git" ]]; then
  git -C "$ROOT" fetch --quiet origin main
  git -C "$ROOT" checkout --quiet main
  git -C "$ROOT" reset --hard --quiet origin/main
else
  git clone --depth 1 "$REPO_URL" "$ROOT"
fi

ln -sfn "$ROOT/tools/holon_gate.py" "$BIN/hfo-holon-gate"
ln -sfn "$ROOT/ops/vps_exec_guard.py" "$BIN/hfo-vps-exec"
chmod +x "$ROOT/tools/holon_gate.py" "$ROOT/ops/vps_exec_guard.py"

python3 -m unittest discover -s "$ROOT/tests" -p 'test_holon_gate.py'

commit="$(git -C "$ROOT" rev-parse HEAD)"
python3 - "$STATE/install.json" "$commit" <<'PY'
import json, platform, sys
from datetime import datetime, timezone
from pathlib import Path
p=Path(sys.argv[1])
p.write_text(json.dumps({
  'schema':'hfo.forcing-install.v1',
  'observed_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
  'repo_commit':sys.argv[2],
  'platform':{'system':platform.system(),'machine':platform.machine()},
  'semantic_owner':'hfo-sigrun-va-r0',
  'note':'rootless gates only; no scheduler/queue/lease/state owner installed'
},sort_keys=True)+'\n',encoding='utf-8')
PY

echo "ADMIT: installed hfo-holon-gate + hfo-vps-exec at commit $commit"
echo "No service or scheduler was created. Existing Sigrun DO remains semantic owner."
