#!/usr/bin/env python3
"""Bounded FJSPlib CP-SAT crown assay worker.

Uses an immutable public instance URL and a hard makespan threshold. This worker
produces candidate evidence only; external crown/promotion requires an independent
verifier and third-party keeper acceptance.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def ensure_ortools():
    try:
        from ortools.sat.python import cp_model
        return cp_model
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "ortools==9.14.6206"], check=True)
        from ortools.sat.python import cp_model
        return cp_model


def verify(instance: dict, schedule: list[dict], target: int) -> tuple[bool, str]:
    by_op = {row["operation"]: row for row in schedule}
    op_ids = {r["operation"] for r in instance["operations"]}
    if set(by_op) != op_ids:
        return False, "OPERATION_COVERAGE"
    allowed = defaultdict(set)
    for r in instance["operations"]:
        allowed[r["operation"]].add((r["machine"], r["duration"]))
    for op, r in by_op.items():
        if (r["machine"], r["duration"]) not in allowed[op]:
            return False, f"MACHINE_OR_DURATION:{op}"
        if r["end"] - r["start"] != r["duration"] or r["start"] < 0 or r["end"] > target:
            return False, f"TIME_DOMAIN:{op}"
    for p in instance["precedences"]:
        if by_op[p["after"]]["start"] < by_op[p["before"]]["end"]:
            return False, f"PRECEDENCE:{p['before']}:{p['after']}"
    machines = defaultdict(list)
    for r in schedule:
        machines[r["machine"]].append(r)
    for m, rows in machines.items():
        rows.sort(key=lambda x: (x["start"], x["end"], x["operation"]))
        for a, b in zip(rows, rows[1:]):
            if b["start"] < a["end"]:
                return False, f"OVERLAP:{m}:{a['operation']}:{b['operation']}"
    return True, "PASS"


def main() -> int:
    task_path, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    task = json.loads(task_path.read_text(encoding="utf-8"))
    outdir.mkdir(parents=True, exist_ok=True)
    cp_model = ensure_ortools()
    url = task["instance_url"]
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read()
    instance = json.loads(raw)
    source_sha = sha256_bytes(raw)
    if source_sha != task["instance_sha256"]:
        raise RuntimeError(f"INSTANCE_HASH_DRIFT:{source_sha}")
    target = int(task["target_makespan"])
    limit = min(float(task.get("max_seconds", 300)), 330.0)
    seed = int(task.get("seed", 1))

    ops = defaultdict(list)
    for row in instance["operations"]:
        ops[row["operation"]].append((row["machine"], row["duration"]))
    model = cp_model.CpModel()
    start, end, choice, by_machine = {}, {}, {}, defaultdict(list)
    for op in sorted(ops):
        s = model.new_int_var(0, target, f"s{op}")
        e = model.new_int_var(0, target, f"e{op}")
        start[op], end[op] = s, e
        lits = []
        for idx, (machine, duration) in enumerate(ops[op]):
            lit = model.new_bool_var(f"x{op}_{idx}_m{machine}")
            interval = model.new_optional_interval_var(s, duration, e, lit, f"i{op}_{idx}_m{machine}_d{duration}")
            by_machine[machine].append(interval)
            choice[op, idx] = (lit, machine, duration)
            lits.append(lit)
        model.add_exactly_one(lits)
    for intervals in by_machine.values():
        model.add_no_overlap(intervals)
    for p in instance["precedences"]:
        model.add(start[p["after"]] >= end[p["before"]])
    for e in end.values():
        model.add(e <= target)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = limit
    solver.parameters.num_search_workers = max(2, int(task.get("workers", 2)))
    solver.parameters.random_seed = seed
    solver.parameters.randomize_search = True
    solver.parameters.use_lns = True
    t0 = time.time()
    status = solver.solve(model)
    elapsed = time.time() - t0
    status_name = solver.status_name(status)
    schedule = []
    verified = False
    verify_reason = "NO_SOLUTION"
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        for op in sorted(ops):
            selected = [(machine, duration) for idx in range(len(ops[op])) for lit, machine, duration in [choice[op, idx]] if solver.value(lit)]
            if len(selected) != 1:
                raise RuntimeError(f"CHOICE_CARDINALITY:{op}:{selected}")
            machine, duration = selected[0]
            schedule.append({"operation": op, "machine": machine, "start": solver.value(start[op]), "end": solver.value(end[op]), "duration": duration})
        verified, verify_reason = verify(instance, schedule, target)
        (outdir / "schedule.json").write_text(json.dumps(schedule, sort_keys=True, indent=2), encoding="utf-8")
    evidence = {
        "schema": "hfo.fjsp-crown-result.v1",
        "work_id": task["work_id"],
        "instance": instance["instance"],
        "instance_sha256": source_sha,
        "target_makespan": target,
        "solver": "OR-Tools CP-SAT 9.14.6206",
        "seed": seed,
        "status": status_name,
        "elapsed_s": round(elapsed, 3),
        "conflicts": solver.num_conflicts,
        "branches": solver.num_branches,
        "candidate_verified_internal": verified,
        "verify_reason": verify_reason,
        "crown_claim": False,
        "claim_ceiling": "SUBMISSION_READY_INTERNAL_ONLY" if verified else "BOUNDED_SEARCH_RESULT_ONLY",
        "sources": [{"url": url, "sha256": source_sha}],
    }
    result_sha = hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    evidence["result_sha256"] = result_sha
    (outdir / "result.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    report = (
        f"## FJSPLIB CROWN ASSAY — {instance['instance']}\n\n"
        f"- WorkItem: `{task['work_id']}`\n- target: `{target}`\n- status: `{status_name}`\n"
        f"- elapsed_s: `{elapsed:.3f}`\n- internal deterministic verification: `{verified}` (`{verify_reason}`)\n"
        f"- result_sha256: `{result_sha}`\n- claim ceiling: `{evidence['claim_ceiling']}`\n\n"
        "No external submission or crown claim was made. Third-party acceptance remains required.\n"
    )
    (outdir / "report.md").write_text(report, encoding="utf-8")
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
