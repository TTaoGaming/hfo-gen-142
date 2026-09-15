#!/usr/bin/env python3
"""Independent verifier/packetizer for Packomania Evo R3.

No imports from the producer or donor solver. Re-fetches keeper state, applies a
small deterministic radius safety shrink, verifies exact written decimal geometry,
and only then marks strict improvements SUBMISSION_READY_INTERNAL.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 80
KEEPER_URL = "https://www.packomania.com/csqv/txt/sumradii.txt"
SHRINK = Decimal("0.0000000001000001")
BATCH_ID = "packomania-evo-r3-5f8f7e1b"
CARRIER_UUID = "5f8f7e1b-9e2c-4f8c-b2aa-7d34a9e6c11d"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "HFO-Gen142-Packomania-Verifier-R3"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_keeper(raw: bytes) -> dict[int, Decimal]:
    rec: dict[int, Decimal] = {}
    for line in raw.decode("utf-8", errors="strict").splitlines():
        p = line.split()
        if len(p) == 2 and p[0].isdigit():
            rec[int(p[0])] = Decimal(p[1])
    return rec


def parse_candidate(path: Path) -> tuple[int, list[tuple[Decimal, Decimal, Decimal]]]:
    data = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal, parse_int=int)
    n = int(data["n"])
    circles = []
    for row in data["circles"]:
        if len(row) != 3:
            raise ValueError("CIRCLE_SHAPE")
        x, y, r = (Decimal(str(v)) if not isinstance(v, Decimal) else v for v in row)
        circles.append((x, y, r))
    if len(circles) != n:
        raise ValueError("COUNT_MISMATCH")
    return n, circles


def verify_and_shrink(circles: list[tuple[Decimal, Decimal, Decimal]]) -> dict:
    safe: list[tuple[Decimal, Decimal, Decimal]] = []
    for x, y, r in circles:
        rr = r - SHRINK
        if rr <= 0:
            raise ValueError("NONPOSITIVE_AFTER_SHRINK")
        safe.append((x, y, rr))
    min_wall = Decimal("Infinity")
    for x, y, r in safe:
        if not (Decimal(0) <= x <= Decimal(1) and Decimal(0) <= y <= Decimal(1)):
            raise ValueError("CENTER_OUT_OF_BOX")
        w = min(x - r, Decimal(1) - x - r, y - r, Decimal(1) - y - r)
        min_wall = min(min_wall, w)
    min_pair = Decimal("Infinity")
    for i in range(len(safe)):
        xi, yi, ri = safe[i]
        for j in range(i + 1, len(safe)):
            xj, yj, rj = safe[j]
            d = ((xi - xj) * (xi - xj) + (yi - yj) * (yi - yj)).sqrt()
            min_pair = min(min_pair, d - ri - rj)
    if min_wall < 0 or min_pair < 0:
        raise ValueError(f"INFEASIBLE:wall={min_wall}:pair={min_pair}")
    score = sum((r for _, _, r in safe), Decimal(0))
    return {"safe": safe, "score": score, "min_wall": min_wall, "min_pair": min_pair}


def to_pck(circles: list[tuple[Decimal, Decimal, Decimal]], author: str) -> str:
    cs = sorted(circles, key=lambda c: c[2])
    lines = [format(cs[-1][2], ".16f"), author]
    for x, y, r in cs:
        lines.append(f"{x - Decimal('0.5'):.16f} {y - Decimal('0.5'):.16f} {r:.16f}")
    return "\n".join(lines) + "\n"


def main() -> int:
    root = Path(os.environ.get("PACKOMANIA_EVO_OUT", "packomania-evo-r3-out"))
    receipt_path = root / "producer_receipt.json"
    producer_bytes = receipt_path.read_bytes()
    producer = json.loads(producer_bytes)
    if producer.get("batch_id") != BATCH_ID or producer.get("carrier_uuid") != CARRIER_UUID:
        raise RuntimeError("PRODUCER_IDENTITY_MISMATCH")

    keeper_raw = fetch(KEEPER_URL)
    (root / "keeper-verify.txt").write_bytes(keeper_raw)
    keeper = parse_keeper(keeper_raw)
    keeper_sha = sha(keeper_raw)

    verified = []
    winners = []
    best_by_n = producer.get("best_by_n", {})
    for ns, row in sorted(best_by_n.items(), key=lambda kv: int(kv[0])):
        n = int(ns)
        if n in (120, 122):
            raise RuntimeError("ACTIVE_CANDIDATE_DUPLICATION_REFUSED")
        if n not in keeper:
            raise RuntimeError(f"KEEPER_MISSING:{n}")
        candidate_path = root / row["candidate_path"]
        cn, circles = parse_candidate(candidate_path)
        if cn != n:
            raise RuntimeError("CANDIDATE_N_MISMATCH")
        try:
            v = verify_and_shrink(circles)
            score = v["score"]
            incumbent = keeper[n]
            margin = score - incumbent
            status = "STRICT_WIN" if margin > 0 else "VERIFIED_NONWIN"
            pck_sha = None
            pck_name = None
            if margin > 0:
                pck_name = f"csqv{n}.pck"
                pck = to_pck(v["safe"], "Tommy Tai / HFO Gen142; solver: Discovery Loop by Wes Sander")
                p = root / pck_name
                p.write_text(pck, encoding="utf-8")
                pck_sha = sha(p.read_bytes())
                winners.append({
                    "n": n,
                    "score": str(score),
                    "incumbent": str(incumbent),
                    "margin": str(margin),
                    "pck": pck_name,
                    "pck_sha256": pck_sha,
                    "min_wall": str(v["min_wall"]),
                    "min_pair": str(v["min_pair"]),
                    "source_candidate_sha256": row.get("candidate_sha256"),
                    "source_stage": row.get("stage"),
                    "source_seed": row.get("seed"),
                })
            verified.append({
                "n": n,
                "status": status,
                "score_after_safety_shrink": str(score),
                "incumbent_fresh": str(incumbent),
                "margin": str(margin),
                "min_wall": str(v["min_wall"]),
                "min_pair": str(v["min_pair"]),
                "pck_sha256": pck_sha,
            })
        except Exception as exc:
            verified.append({"n": n, "status": "KILLED_BY_VERIFIER", "reason": f"{type(exc).__name__}:{exc}"})

    verifier_sha = sha(Path(__file__).read_bytes())
    core = {
        "schema": "hfo.packomania-evo-verifier.v1",
        "batch_id": BATCH_ID,
        "carrier_uuid": CARRIER_UUID,
        "battlefield": "Packomania csqv",
        "producer_receipt_sha256": sha(producer_bytes),
        "solver_sha256": producer["solver_sha256"],
        "keeper_start_sha256": producer["keeper_start_sha256"],
        "keeper_verify_sha256": keeper_sha,
        "verifier_sha256": verifier_sha,
        "safety_shrink_each_radius": str(SHRINK),
        "evaluations": verified,
        "winners": winners,
        "public_crown_threshold_met_locally": bool(winners),
        "status": "SUBMISSION_READY_INTERNAL" if winners else "NO_NEW_RECORD",
        "claim_ceiling": "CANDIDATE_RECORD_PENDING_THIRD_PARTY_ACCEPTANCE" if winners else "NO_NEW_RECORD",
        "external_submission_performed": False,
        "tao_hot_loop_actions": 0,
    }
    replay = json.dumps(core, sort_keys=True, separators=(",", ":")).encode()
    core["replay_sha256"] = sha(replay)
    (root / "verifier_receipt.json").write_text(json.dumps(core, indent=2), encoding="utf-8")

    if winners:
        lines = [
            "# SUBMISSION_READY_INTERNAL — Packomania csqv Evo R3",
            "",
            "External submission has NOT been performed. Re-fetch the keeper immediately before human send.",
            "",
            f"- batch: `{BATCH_ID}`",
            f"- carrier: `{CARRIER_UUID}`",
            f"- donor: `ucsandman/discovery-loop@{producer['parent_donor'].split('@',1)[1].split(':',1)[0]}`",
            f"- verifier replay: `{core['replay_sha256']}`",
            "",
            "## Strict locally verified improvements",
        ]
        for w in winners:
            lines.append(f"- N={w['n']}: safe Σr `{w['score']}` vs fresh keeper `{w['incumbent']}` (Δ `{w['margin']}`), `{w['pck']}` SHA256 `{w['pck_sha256']}`")
        lines += [
            "",
            "Claim ceiling until keeper acceptance: `CANDIDATE_RECORD_PENDING_THIRD_PARTY_ACCEPTANCE`.",
        ]
        (root / "SUBMISSION_READY_INTERNAL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"batch_id": BATCH_ID, "status": core["status"], "winner_count": len(winners), "replay_sha256": core["replay_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
