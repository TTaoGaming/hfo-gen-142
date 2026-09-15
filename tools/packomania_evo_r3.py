#!/usr/bin/env python3
"""Bounded Packomania csqv evolutionary producer.

Frozen donor only proposes candidates. This file does NOT certify material wins;
verification is owned by packomania_verify_r3.py in a separate downstream job.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

DONOR_COMMIT = "ce97256043f7813e0beaeeb7ca5cafacbf77fbdb"
SOLVER_URL = f"https://raw.githubusercontent.com/ucsandman/discovery-loop/{DONOR_COMMIT}/best/solver.py"
KEEPER_URL = "https://www.packomania.com/csqv/txt/sumradii.txt"
BATCH_ID = "packomania-evo-r3-5f8f7e1b"
CARRIER_UUID = "5f8f7e1b-9e2c-4f8c-b2aa-7d34a9e6c11d"
# Explicitly exclude the already-packaged N=120/N=122 crown candidates.
TARGETS = [116, 117, 118, 119, 121, 123, 124, 125]
STAGE1_SECONDS = 12
STAGE2_SECONDS = 30
STAGE2_SURVIVORS = 3


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "HFO-Gen142-Packomania-Evo-R3"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_keeper(raw: bytes) -> dict[int, float]:
    rec: dict[int, float] = {}
    for line in raw.decode("utf-8", errors="strict").splitlines():
        p = line.split()
        if len(p) == 2 and p[0].isdigit():
            rec[int(p[0])] = float(p[1])
    missing = [n for n in TARGETS if n not in rec]
    if missing:
        raise RuntimeError(f"KEEPER_PARSE_MISSING:{missing}")
    return rec


def run_one(solver: Path, outdir: Path, n: int, seconds: int, seed: int, stage: str, keeper: dict[int, float]) -> dict:
    out = outdir / f"{stage}-n{n}-seed{seed}.json"
    t0 = time.time()
    cp = subprocess.run(
        [sys.executable, str(solver), "--n", str(n), "--time", str(seconds), "--seed", str(seed), "--out", str(out)],
        text=True,
        capture_output=True,
        timeout=seconds + 45,
    )
    elapsed = time.time() - t0
    row = {
        "stage": stage,
        "n": n,
        "seed": seed,
        "seconds_budget": seconds,
        "elapsed_seconds": round(elapsed, 3),
        "returncode": cp.returncode,
        "candidate_path": out.name,
        "stdout_tail": cp.stdout[-1000:],
        "stderr_tail": cp.stderr[-1000:],
        "incumbent_at_producer_start": keeper[n],
    }
    if cp.returncode != 0 or not out.exists():
        row.update({"candidate_sum": None, "margin": None, "producer_status": "NO_CANDIDATE"})
        return row
    try:
        data = json.loads(out.read_text(encoding="utf-8"))
        score = float(data["sum"])
        if int(data["n"]) != n or len(data.get("circles", [])) != n:
            raise ValueError("shape")
        row.update({
            "candidate_sum": score,
            "margin": score - keeper[n],
            "producer_status": "CANDIDATE_UNVERIFIED",
            "candidate_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        })
    except Exception as exc:
        row.update({"candidate_sum": None, "margin": None, "producer_status": f"MALFORMED:{type(exc).__name__}"})
    return row


def main() -> int:
    outdir = Path(os.environ.get("PACKOMANIA_EVO_OUT", "packomania-evo-r3-out"))
    outdir.mkdir(parents=True, exist_ok=True)

    solver_bytes = fetch(SOLVER_URL)
    solver = outdir / "frozen_solver.py"
    solver.write_bytes(solver_bytes)
    solver_sha = sha256_bytes(solver_bytes)

    keeper_raw = fetch(KEEPER_URL)
    (outdir / "keeper-start.txt").write_bytes(keeper_raw)
    keeper_sha = sha256_bytes(keeper_raw)
    keeper = parse_keeper(keeper_raw)

    rows: list[dict] = []
    for n in TARGETS:
        rows.append(run_one(solver, outdir, n, STAGE1_SECONDS, 315000 + n, "s1", keeper))

    viable = [r for r in rows if r.get("candidate_sum") is not None]
    viable.sort(key=lambda r: (float(r.get("margin") or -1e99), float(r["candidate_sum"])), reverse=True)
    survivors = [int(r["n"]) for r in viable[:STAGE2_SURVIVORS]]

    for n in survivors:
        rows.append(run_one(solver, outdir, n, STAGE2_SECONDS, 415000 + n, "s2", keeper))

    # Producer ranking is search control only, never crown truth.
    best_by_n: dict[int, dict] = {}
    for r in rows:
        if r.get("candidate_sum") is None:
            continue
        n = int(r["n"])
        if n not in best_by_n or float(r["candidate_sum"]) > float(best_by_n[n]["candidate_sum"]):
            best_by_n[n] = r

    receipt = {
        "schema": "hfo.packomania-evo-producer.v1",
        "batch_id": BATCH_ID,
        "carrier_uuid": CARRIER_UUID,
        "battlefield": "Packomania csqv",
        "parent_donor": f"ucsandman/discovery-loop@{DONOR_COMMIT}:best/solver.py",
        "solver_sha256": solver_sha,
        "keeper_url": KEEPER_URL,
        "keeper_start_sha256": keeper_sha,
        "excluded_active_candidates": [120, 122],
        "mutation_axes": [
            "target_n",
            "rng_seed",
            "time_budget_successive_halving",
            "donor_internal_island_basin_hopping_population",
        ],
        "stage1_seconds": STAGE1_SECONDS,
        "stage2_seconds": STAGE2_SECONDS,
        "stage2_survivors": survivors,
        "evaluations": rows,
        "best_by_n": {str(k): v for k, v in sorted(best_by_n.items())},
        "producer_claim_ceiling": "CANDIDATE_UNVERIFIED",
        "external_effect": False,
        "tao_hot_loop_actions": 0,
    }
    canon = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canon).hexdigest()
    (outdir / "producer_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps({"batch_id": BATCH_ID, "survivors": survivors, "evaluations": len(rows), "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
