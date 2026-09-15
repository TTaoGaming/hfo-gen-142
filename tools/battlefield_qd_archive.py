#!/usr/bin/env python3
"""Deterministic QD/MOME-style archive for admitted battlefield cards.

This tool is exploration policy, not a submission reducer. It reuses the existing
battlefield gate, derives stable behavioral niches, and preserves a Pareto set of
champions inside each niche. It deliberately emits no global primary.

Durable demand/leases/wakes remain owned by the incumbent GitHub/Cloudflare
control plane; this module is a pure projection over versioned battlefield cards.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

from battlefield_reduce import evaluate_path

SCHEMA = "hfo.battlefield-qd-archive.v1"
OBJECTIVE_NAMES = (
    "routing_score",
    "prestige",
    "buyer_legibility",
    "p_beat_incumbent",
    "p_public_proof_7d",
    "canary_efficiency",
)
PRESTIGE = {"S": 1.0, "A": 0.9, "B": 0.75, "C": 0.5, "D": 0.25}


def _f(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def proof_band(hours: float) -> str:
    if hours <= 1:
        return "IMMEDIATE"
    if hours <= 24:
        return "SAME_DAY"
    if hours <= 168:
        return "THIS_WEEK"
    return "LONG_HORIZON"


def compute_band(runtime_minutes: float, cost_usd: float) -> str:
    # Cost is converted to an approximate operator-independent compute burden.
    burden = runtime_minutes + 15.0 * cost_usd
    if burden <= 180:
        return "LIGHT"
    if burden <= 900:
        return "MEDIUM"
    return "HEAVY"


def niche_descriptor(card: dict) -> dict:
    target = card.get("target") or {}
    prestige = card.get("prestige") or {}
    canary = (card.get("evolution") or {}).get("canary") or {}
    verifier = "INDEPENDENT_PUBLIC" if (
        prestige.get("independent_verifier") is True and prestige.get("public_attribution") is True
    ) else "OTHER"
    return {
        "domain": str(card.get("domain") or "UNKNOWN"),
        "proof_band": proof_band(_f(target.get("proof_latency_hours"), 1e9)),
        "compute_band": compute_band(_f(canary.get("runtime_minutes"), 1e9), _f(canary.get("cost_usd"), 1e9)),
        "verifier_band": verifier,
    }


def niche_key(desc: dict) -> str:
    return "::".join(str(desc[k]) for k in ("domain", "proof_band", "compute_band", "verifier_band"))


def objective_vector(card: dict, gate_receipt: dict) -> dict[str, float]:
    prestige = card.get("prestige") or {}
    probability = card.get("probability") or {}
    canary = (card.get("evolution") or {}).get("canary") or {}
    runtime = max(0.0, _f(canary.get("runtime_minutes"), 1e6))
    cost = max(0.0, _f(canary.get("cost_usd"), 1e6))
    efficiency = 1.0 / (1.0 + runtime / 60.0 + cost / 10.0)
    return {
        "routing_score": _f(gate_receipt.get("routing_score")),
        "prestige": PRESTIGE.get(str(prestige.get("tier") or "").upper(), 0.0),
        "buyer_legibility": _f(prestige.get("buyer_legibility")),
        "p_beat_incumbent": _f(probability.get("p_beat_incumbent")),
        "p_public_proof_7d": _f(probability.get("p_public_proof_7d")),
        "canary_efficiency": efficiency,
    }


def dominates(a: dict[str, float], b: dict[str, float], eps: float = 1e-12) -> bool:
    ge = all(a[k] + eps >= b[k] for k in OBJECTIVE_NAMES)
    gt = any(a[k] > b[k] + eps for k in OBJECTIVE_NAMES)
    return ge and gt


def pareto_partition(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    front, dominated_rows = [], []
    for i, row in enumerate(rows):
        if any(i != j and dominates(other["objectives"], row["objectives"]) for j, other in enumerate(rows)):
            dominated_rows.append(row)
        else:
            front.append(row)
    return front, dominated_rows


def crowding_distances(rows: list[dict]) -> dict[str, float]:
    if not rows:
        return {}
    ids = [r["battlefield_id"] for r in rows]
    dist = {rid: 0.0 for rid in ids}
    if len(rows) <= 2:
        return {rid: math.inf for rid in ids}
    for key in OBJECTIVE_NAMES:
        ordered = sorted(rows, key=lambda r: (r["objectives"][key], r["battlefield_id"]))
        lo, hi = ordered[0]["objectives"][key], ordered[-1]["objectives"][key]
        dist[ordered[0]["battlefield_id"]] = math.inf
        dist[ordered[-1]["battlefield_id"]] = math.inf
        if hi <= lo:
            continue
        for i in range(1, len(ordered) - 1):
            rid = ordered[i]["battlefield_id"]
            if math.isinf(dist[rid]):
                continue
            prev_v = ordered[i - 1]["objectives"][key]
            next_v = ordered[i + 1]["objectives"][key]
            dist[rid] += (next_v - prev_v) / (hi - lo)
    return dist


def truncate_front(front: list[dict], max_elites: int) -> tuple[list[dict], list[dict]]:
    if len(front) <= max_elites:
        return sorted(front, key=lambda r: r["battlefield_id"]), []
    distances = crowding_distances(front)
    ranked = sorted(
        front,
        key=lambda r: (
            1 if math.isinf(distances[r["battlefield_id"]]) else 0,
            distances[r["battlefield_id"]] if not math.isinf(distances[r["battlefield_id"]]) else 1e18,
            r["objectives"]["routing_score"],
            r["battlefield_id"],
        ),
        reverse=True,
    )
    keep = ranked[:max_elites]
    evict = ranked[max_elites:]
    for row in keep + evict:
        d = distances[row["battlefield_id"]]
        row["crowding_distance"] = "INF" if math.isinf(d) else round(d, 12)
    return sorted(keep, key=lambda r: r["battlefield_id"]), sorted(evict, key=lambda r: r["battlefield_id"])


def archive(paths: list[Path], max_elites_per_niche: int = 4) -> dict:
    if max_elites_per_niche < 1:
        raise ValueError("MAX_ELITES_REFUSED")
    admitted_rows, rejected = [], []
    for path in paths:
        gate_receipt = evaluate_path(path)
        if not gate_receipt.get("admitted"):
            rejected.append(gate_receipt)
            continue
        card = json.loads(Path(path).read_text(encoding="utf-8"))
        desc = niche_descriptor(card)
        admitted_rows.append({
            "battlefield_id": str(card.get("battlefield_id")),
            "path": str(path),
            "stage": card.get("stage"),
            "gate_verdict": gate_receipt.get("verdict"),
            "niche": desc,
            "niche_key": niche_key(desc),
            "objectives": objective_vector(card, gate_receipt),
        })

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in admitted_rows:
        grouped[row["niche_key"]].append(row)

    niches = []
    total_champions = 0
    for key in sorted(grouped):
        rows = grouped[key]
        front, dominated_rows = pareto_partition(rows)
        champions, crowding_evicted = truncate_front(front, max_elites_per_niche)
        total_champions += len(champions)
        niches.append({
            "niche_key": key,
            "descriptor": rows[0]["niche"],
            "population": len(rows),
            "champions": champions,
            "dominated_evidence": sorted(dominated_rows, key=lambda r: r["battlefield_id"]),
            "crowding_evicted": crowding_evicted,
            "underfilled": len(champions) < max_elites_per_niche,
        })

    return {
        "schema": SCHEMA,
        "mode": "EXPLORE_QD_MOME",
        "collapse_forbidden": True,
        "global_primary": None,
        "objective_names": list(OBJECTIVE_NAMES),
        "max_elites_per_niche": max_elites_per_niche,
        "admitted_candidates": len(admitted_rows),
        "niche_count": len(niches),
        "champion_count": total_champions,
        "niches": niches,
        "rejected": rejected,
        "next_search_pressure": [n["niche_key"] for n in niches if n["underfilled"]],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a diversity-preserving battlefield archive; never emits a global primary")
    ap.add_argument("cards", nargs="+")
    ap.add_argument("--max-elites-per-niche", type=int, default=4)
    args = ap.parse_args()
    paths = [Path(p) for p in args.cards if not Path(p).name.startswith("_")]
    try:
        result = archive(paths, args.max_elites_per_niche)
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": SCHEMA, "mode": "HOLD", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0 if result["champion_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
