#!/usr/bin/env python3
"""Deterministic quality-diversity archive for battlefield exploration.

EXPLORE is illumination, not winner-take-all selection. Every admitted card is
placed in a deterministic behavior-space cell. Each cell keeps a bounded
Pareto set, with crowding-distance truncation when necessary. There is no
global primary in this mode.

This is a reducer/selection policy only. It owns no scheduler, queue, lease,
credentials, external effects, or authority.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import math
import re
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("battlefield_gate", ROOT / "tools" / "battlefield_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)

OBJECTIVE_KEYS = (
    "routing_score",
    "p_beat_incumbent",
    "p_public_proof_7d",
    "buyer_legibility",
    "canary_efficiency",
)


def _slug(value: Any) -> str:
    text = str(value or "unknown").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "unknown"


def _search_regime(card: dict[str, Any]) -> str:
    axes = " ".join(card.get("evolution", {}).get("mutable_axes", [])).lower()
    # Deterministic first-match taxonomy. The buckets are intentionally broad:
    # behavior-space diversity matters more than lexical precision.
    buckets = (
        ("geometry", ("geometry", "packing", "coordinate", "placement", "shape", "mesh")),
        ("systems-kernel", ("kernel", "compiler", "cache", "vector", "parallel", "runtime", "latency", "memory movement", "tensor-layout")),
        ("model-ensemble", ("model", "ensemble", "architecture", "feature", "loss", "augmentation", "checkpoint", "fine-tuning")),
        ("prompt-policy", ("prompt", "policy", "instruction", "context", "memory", "tool selection", "reasoning")),
        ("scheduling-routing", ("schedule", "scheduling", "routing", "route", "makespan", "dispatch", "allocation")),
        ("algorithm-search", ("algorithm", "heuristic", "optimizer", "search", "mutation", "cma", "pso", "gradient", "solver")),
    )
    for label, needles in buckets:
        if any(n in axes for n in needles):
            return label
    return "other"


def _proof_clock(hours: float) -> str:
    if hours <= 1:
        return "immediate"
    if hours <= 24:
        return "day"
    if hours <= 168:
        return "week"
    return "slow"


def _compute_regime(card: dict[str, Any]) -> str:
    execution = card.get("execution", {})
    haystack = " ".join(
        str(execution.get(k, "")) for k in ("provider_class", "provider_route", "carrier")
    ).lower()
    if execution.get("frontier_required"):
        return "frontier-model"
    if any(k in haystack for k in ("gpu", "cuda", "tpu", "npu", "accelerator", "training")):
        return "accelerator"
    if execution.get("local_reproduction_ready"):
        return "local-repro"
    return "remote-or-mixed"


def behavior_descriptor(card: dict[str, Any]) -> dict[str, str]:
    target = card.get("target", {})
    descriptor = {
        "domain_family": _slug(card.get("domain")),
        "search_regime": _search_regime(card),
        "proof_clock": _proof_clock(float(target.get("proof_latency_hours", 9999))),
        "compute_regime": _compute_regime(card),
    }
    descriptor["cell_id"] = "::".join(descriptor[k] for k in (
        "domain_family", "search_regime", "proof_clock", "compute_regime"
    ))
    return descriptor


def objective_vector(card: dict[str, Any], routing_score: float) -> dict[str, float]:
    probability = card.get("probability", {})
    prestige = card.get("prestige", {})
    canary = card.get("evolution", {}).get("canary", {})
    runtime = max(0.0, float(canary.get("runtime_minutes", 0.0)))
    cost = max(0.0, float(canary.get("cost_usd", 0.0)))
    # A bounded monotonic efficiency objective. It is a diversity/selection aid,
    # not evidence and not a substitute for the frozen external evaluator.
    efficiency = 1.0 / (1.0 + cost + runtime / 60.0)
    return {
        "routing_score": float(routing_score),
        "p_beat_incumbent": float(probability.get("p_beat_incumbent", 0.0)),
        "p_public_proof_7d": float(probability.get("p_public_proof_7d", 0.0)),
        "buyer_legibility": float(prestige.get("buyer_legibility", 0.0)),
        "canary_efficiency": efficiency,
    }


def dominates(a: dict[str, float], b: dict[str, float]) -> bool:
    ge_all = all(a[k] >= b[k] for k in OBJECTIVE_KEYS)
    gt_any = any(a[k] > b[k] for k in OBJECTIVE_KEYS)
    return ge_all and gt_any


def pareto_front(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    front = []
    for candidate in entries:
        if not any(
            other is not candidate and dominates(other["objectives"], candidate["objectives"])
            for other in entries
        ):
            front.append(candidate)
    return sorted(front, key=lambda e: (e["battlefield_id"], e["path"]))


def crowding_distance(entries: list[dict[str, Any]]) -> dict[str, float]:
    """NSGA-style crowding distance used only to truncate a dense cell."""
    if not entries:
        return {}
    distance = {e["entry_id"]: 0.0 for e in entries}
    if len(entries) <= 2:
        return {e["entry_id"]: math.inf for e in entries}
    for key in OBJECTIVE_KEYS:
        ordered = sorted(entries, key=lambda e: (e["objectives"][key], e["entry_id"]))
        lo = ordered[0]["objectives"][key]
        hi = ordered[-1]["objectives"][key]
        distance[ordered[0]["entry_id"]] = math.inf
        distance[ordered[-1]["entry_id"]] = math.inf
        if hi == lo:
            continue
        for idx in range(1, len(ordered) - 1):
            eid = ordered[idx]["entry_id"]
            if math.isinf(distance[eid]):
                continue
            prev_v = ordered[idx - 1]["objectives"][key]
            next_v = ordered[idx + 1]["objectives"][key]
            distance[eid] += (next_v - prev_v) / (hi - lo)
    return distance


def truncate_by_crowding(entries: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if len(entries) <= limit:
        return entries
    distances = crowding_distance(entries)
    ranked = sorted(
        entries,
        key=lambda e: (
            -distances[e["entry_id"]],
            -e["objectives"]["routing_score"],
            e["battlefield_id"],
            e["path"],
        ),
    )
    return sorted(ranked[:limit], key=lambda e: (e["battlefield_id"], e["path"]))


def evaluate_path(path: Path) -> dict[str, Any]:
    try:
        card = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"path": str(path), "admitted": False, "verdict": "INVALID_JSON", "error": str(exc)}
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = gate.evaluate(card)
    try:
        receipt = json.loads(buf.getvalue().strip().splitlines()[-1])
    except Exception:
        receipt = {"decision": "HOLD", "verdict": "GATE_RECEIPT_UNREADABLE"}
    admitted = rc == 0 and receipt.get("decision") == "ADMIT"
    out: dict[str, Any] = {
        "path": str(path),
        "battlefield_id": card.get("battlefield_id"),
        "admitted": admitted,
        "verdict": receipt.get("verdict"),
        "routing_score": float(receipt.get("routing_score", 0.0)),
    }
    if admitted:
        out["descriptor"] = behavior_descriptor(card)
        out["objectives"] = objective_vector(card, out["routing_score"])
        out["card"] = card
    return out


def _public_entry(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "battlefield_id": raw["battlefield_id"],
        "path": raw["path"],
        "gate_verdict": raw["verdict"],
        "descriptor": raw["descriptor"],
        "objectives": raw["objectives"],
    }


def illuminate(paths: list[Path], max_elites_per_niche: int = 2) -> dict[str, Any]:
    if max_elites_per_niche < 1:
        raise ValueError("max_elites_per_niche must be >=1")
    evaluated = [evaluate_path(Path(p)) for p in paths]
    admitted = [e for e in evaluated if e.get("admitted")]
    rejected = [
        {k: v for k, v in e.items() if k != "card"}
        for e in evaluated if not e.get("admitted")
    ]

    by_cell: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in admitted:
        identity = str(e["battlefield_id"]) + "\0" + str(e["path"])
        e["entry_id"] = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        by_cell[e["descriptor"]["cell_id"]].append(e)

    archive = []
    crowded_cells = []
    all_elites = []
    for cell_id in sorted(by_cell):
        candidates = by_cell[cell_id]
        front = pareto_front(candidates)
        elites = truncate_by_crowding(front, max_elites_per_niche)
        if len(candidates) > max_elites_per_niche:
            crowded_cells.append(cell_id)
        public_elites = [_public_entry(e) for e in elites]
        all_elites.extend(public_elites)
        archive.append({
            "cell_id": cell_id,
            "descriptor": candidates[0]["descriptor"],
            "candidate_count": len(candidates),
            "pareto_count": len(front),
            "elites": public_elites,
        })

    def unique_count(field: str) -> int:
        return len({e["descriptor"][field] for e in admitted})

    occupancy = Counter(e["descriptor"]["cell_id"] for e in admitted)
    result = {
        "decision": "ILLUMINATE" if admitted else "NONE",
        "mode": "QD_EXPLORE",
        "primary": None,
        "selection_pressure": "COVERAGE_PLUS_PER_NICHE_PARETO",
        "coverage": {
            "admitted_candidates": len(admitted),
            "occupied_niches": len(by_cell),
            "elite_count": len(all_elites),
            "domain_families": unique_count("domain_family") if admitted else 0,
            "search_regimes": unique_count("search_regime") if admitted else 0,
            "proof_clocks": unique_count("proof_clock") if admitted else 0,
            "compute_regimes": unique_count("compute_regime") if admitted else 0,
            "max_cell_occupancy": max(occupancy.values(), default=0),
            "crowded_niches": crowded_cells,
        },
        "archive": archive,
        "rejected": rejected,
        "poka_yoke": {
            "global_primary_forbidden": True,
            "crowded_cell_action": "MORPH_TO_DIFFERENT_QD_CELL_UNLESS_DISTINCT_PAIRED_VERIFIER",
            "send_gate": "Use battlefield_reduce.py only in explicit SEND phase",
        },
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["archive_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a QD/MOME battlefield archive without global convergence")
    parser.add_argument("cards", nargs="+")
    parser.add_argument("--max-elites-per-niche", type=int, default=2)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.max_elites_per_niche <= 8:
        print(json.dumps({"decision": "HOLD", "verdict": "QD_ELITE_LIMIT_INVALID"}, sort_keys=True))
        return 2
    paths = [Path(p) for p in args.cards if not Path(p).name.startswith("_")]
    if not paths:
        print(json.dumps({"decision": "NONE", "mode": "QD_EXPLORE", "primary": None}, sort_keys=True))
        return 1
    out = illuminate(paths, args.max_elites_per_niche)
    print(json.dumps(out, sort_keys=True, indent=2 if args.pretty else None))
    return 0 if out["decision"] == "ILLUMINATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
