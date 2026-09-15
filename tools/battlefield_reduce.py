#!/usr/bin/env python3
"""Deterministic FINAL/SEND reducer for admitted battlefield cards.

This is intentionally a convergence operator: it outputs at most three
survivors and exactly one primary, or NONE. It MUST NOT be used during QD
exploration; use qd_battlefield_archive.py for EXPLORE.
Uses battlefield_gate as the sole admission/scoring authority.
"""
import argparse
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("battlefield_gate", ROOT / "tools" / "battlefield_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def evaluate_path(path):
    try:
        card = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        return {"path": str(path), "admitted": False, "verdict": "INVALID_JSON", "error": str(exc)}
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = gate.evaluate(card)
    try:
        receipt = json.loads(buf.getvalue().strip().splitlines()[-1])
    except Exception:
        receipt = {"decision": "HOLD", "verdict": "GATE_RECEIPT_UNREADABLE"}
    return {
        "path": str(path),
        "battlefield_id": card.get("battlefield_id"),
        "stage": card.get("stage"),
        "admitted": rc == 0 and receipt.get("decision") == "ADMIT",
        "verdict": receipt.get("verdict"),
        "routing_score": float(receipt.get("routing_score", 0.0)),
    }

def reduce(paths, max_survivors=3, phase="EXPLORE"):
    if phase != "SEND":
        return {
            "decision": "HOLD",
            "verdict": "GLOBAL_CONVERGENCE_FORBIDDEN_DURING_EXPLORE",
            "primary": None,
            "survivors": [],
            "rejected": [],
            "next": "Use tools/qd_battlefield_archive.py until an explicit SEND phase is admitted",
        }
    receipts = [evaluate_path(p) for p in paths]
    admitted = [r for r in receipts if r["admitted"]]
    admitted.sort(key=lambda r: (-r["routing_score"], r.get("battlefield_id") or "", r["path"]))
    survivors = admitted[:max_survivors]
    rejected = [r for r in receipts if not r["admitted"]]
    if not survivors:
        return {"decision": "NONE", "primary": None, "survivors": [], "rejected": rejected}
    return {
        "decision": "SELECT",
        "primary": survivors[0],
        "survivors": survivors,
        "rejected": rejected,
    }


def main():
    parser = argparse.ArgumentParser(description="Reduce gated battlefields to <=3 survivors and one primary")
    parser.add_argument("cards", nargs="+")
    parser.add_argument("--max-survivors", type=int, default=3)
    parser.add_argument("--phase", choices=("EXPLORE", "SEND"), default="EXPLORE",
                        help="Poka-yoke: global convergence is legal only in explicit SEND phase")
    args = parser.parse_args()
    if not 1 <= args.max_survivors <= 3:
        print(json.dumps({"decision": "HOLD", "verdict": "SURVIVOR_LIMIT_INVALID"}, sort_keys=True))
        return 1
    paths = [Path(p) for p in args.cards if not Path(p).name.startswith("_")]
    if not paths:
        print(json.dumps({"decision": "NONE", "primary": None, "survivors": [], "rejected": []}, sort_keys=True))
        return 1
    result = reduce(paths, args.max_survivors, phase=args.phase)
    print(json.dumps(result, sort_keys=True))
    if result["decision"] == "HOLD":
        return 2
    return 0 if result["decision"] == "SELECT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
