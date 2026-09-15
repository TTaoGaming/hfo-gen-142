#!/usr/bin/env python3
"""Fail-closed admission probe for a Frontier Fast exact-GB10 fitness worker.

Thin boundary adapter only. It owns no scheduling, provider routing, mutation,
fitness scoring, or submit authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run(*cmd: str) -> dict[str, object]:
    exe = shutil.which(cmd[0])
    if not exe:
        return {"available": False, "argv": list(cmd), "exit_code": None, "stdout": "", "stderr": "COMMAND_MISSING"}
    proc = subprocess.run([exe, *cmd[1:]], text=True, capture_output=True, timeout=15, check=False)
    return {
        "available": True,
        "argv": list(cmd),
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip()[:8000],
        "stderr": proc.stderr.strip()[:4000],
    }


def sha256_file(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-ref", required=True)
    ap.add_argument("--patch-file", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    observed = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    arch = platform.machine().lower()
    nvidia = run("nvidia-smi", "--query-gpu=name,driver_version,memory.total,compute_cap", "--format=csv,noheader")
    nvcc = run("nvcc", "--version")
    uname = run("uname", "-a")
    mem = run("free", "-b")
    disk = run("df", "-B1", str(Path.home()))

    gpu_text = str(nvidia.get("stdout") or "")
    gpu_ok = bool(nvidia.get("available") and nvidia.get("exit_code") == 0 and "GB10" in gpu_text.upper())
    arch_ok = arch in {"aarch64", "arm64"}
    cuda_ok = bool(nvcc.get("available") and nvcc.get("exit_code") == 0)
    exact = arch_ok and gpu_ok and cuda_ok

    receipt = {
        "schema": "hfo.frontier.gb10-worker-probe.v1",
        "observed_utc": observed,
        "source_ref": args.source_ref,
        "patch_sha256": sha256_file(args.patch_file),
        "host": platform.node(),
        "arch": arch,
        "checks": {"arch_aarch64": arch_ok, "gpu_reports_gb10": gpu_ok, "nvcc_available": cuda_ok},
        "nvidia_smi": nvidia,
        "nvcc": nvcc,
        "uname": uname,
        "memory": mem,
        "disk_home": disk,
        "fitness_class": "EXACT_GB10_FITNESS" if exact else "NOT_EXACT_GB10",
        "status": "PASS_EXACT_GB10" if exact else "HOLD_NOT_EXACT_GB10",
        "effect_ceiling": "OBSERVE_ONLY",
        "credential_probe": "NONE",
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    receipt["receipt_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if exact else 20


if __name__ == "__main__":
    raise SystemExit(main())
