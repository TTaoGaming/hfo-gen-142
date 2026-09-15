#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

from ortools.sat.python import cp_model

PIN = "7b3f6fb1384309bd4abca866fe3bef2993139b91"
ROOT = f"https://raw.githubusercontent.com/ScheduleOpt/benchmarks/{PIN}/flexible-jobshop"


def fetch_json(url: str):
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def greedy_machine_hint(by_op, precedences, seed: int):
    """Cheap donor: load-aware randomized machine assignment only.

    We deliberately do not treat this as fitness. It only supplies CP-SAT hints.
    """
    rng = random.Random(seed)
    load = defaultdict(int)
    choice = {}
    # Criticality proxy: sum of minimum durations reachable through precedence DAG.
    succ = defaultdict(list)
    for e in precedences:
        succ[int(e["before"])].append(int(e["after"]))
    memo = {}

    def tail(op):
        if op in memo:
            return memo[op]
        own = min(int(x["duration"]) for x in by_op[op])
        memo[op] = own + max((tail(v) for v in succ[op]), default=0)
        return memo[op]

    for op in sorted(by_op, key=lambda o: (-tail(o), o)):
        opts = list(by_op[op])
        scored = []
        for x in opts:
            m, d = int(x["machine"]), int(x["duration"])
            # Small seeded jitter creates a cheap portfolio while preserving load signal.
            scored.append((load[m] + d + rng.random() * max(1, d) * 0.08, m, d))
        _, m, d = min(scored)
        choice[op] = m
        load[m] += d
    return choice


class ImprovementStopper(cp_model.CpSolverSolutionCallback):
    def __init__(self, target: int):
        super().__init__()
        self.target = target
        self.best = None
        self.hits = 0

    def on_solution_callback(self):
        value = int(round(self.objective_value))
        self.best = value if self.best is None else min(self.best, value)
        self.hits += 1
        if value <= self.target:
            self.stop_search()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instance", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--seconds", type=float, default=600)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--outdir", default="out")
    a = ap.parse_args()

    inst_url = f"{ROOT}/instances/json/{a.instance}.json"
    bks_url = f"{ROOT}/solutions/bks.json"
    inst, inst_sha = fetch_json(inst_url)
    bks, bks_sha = fetch_json(bks_url)
    row = next(x for x in bks if x["instance"] == a.instance)
    published_ub = int(row["upper_bound"])
    published_lb = int(row["lower_bound"])
    target = published_ub - 1
    horizon = published_ub  # R2: first allow rediscovery of the public incumbent.

    by_op = defaultdict(list)
    machines = defaultdict(list)
    for x in inst["operations"]:
        by_op[int(x["operation"])].append(x)

    model = cp_model.CpModel()
    starts, ends, presences = {}, {}, {}
    for op in sorted(by_op):
        starts[op] = model.new_int_var(0, horizon, f"s_{op}")
        ends[op] = model.new_int_var(0, horizon, f"e_{op}")
        ps = []
        for x in by_op[op]:
            m, d = int(x["machine"]), int(x["duration"])
            p = model.new_bool_var(f"op_{op}_m_{m}")
            # Sharing master start/end is exact: the selected optional interval alone
            # enforces end = start + its machine-specific duration.
            iv = model.new_optional_interval_var(starts[op], d, ends[op], p, f"iv_{op}_m_{m}")
            machines[m].append(iv)
            presences[(op, m)] = p
            ps.append(p)
        model.add_exactly_one(ps)

    for e in inst["precedences"]:
        model.add(ends[int(e["before"])] <= starts[int(e["after"])])
    for m in sorted(machines):
        model.add_no_overlap(machines[m])

    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [ends[o] for o in sorted(ends)])
    model.minimize(makespan)

    hint = greedy_machine_hint(by_op, inst["precedences"], a.seed)
    for (op, m), p in presences.items():
        model.add_hint(p, 1 if hint.get(op) == m else 0)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = a.seconds
    solver.parameters.num_search_workers = a.workers
    solver.parameters.random_seed = a.seed
    solver.parameters.randomize_search = True
    solver.parameters.log_search_progress = True
    stopper = ImprovementStopper(target)
    t0 = time.monotonic()
    status = solver.solve(model, stopper)
    elapsed = time.monotonic() - t0
    status_name = solver.status_name(status)

    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "hfo.fjsplib-bks-hunt.v2",
        "instance": a.instance,
        "source_commit": PIN,
        "instance_sha256": inst_sha,
        "bks_sha256": bks_sha,
        "published_lb": published_lb,
        "published_ub": published_ub,
        "target": target,
        "search_horizon": horizon,
        "seed": a.seed,
        "workers": a.workers,
        "status": status_name,
        "wall_time_s": elapsed,
        "solution_count": stopper.hits,
        "best_objective_bound": solver.best_objective_bound if status in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.UNKNOWN) else None,
        "objective": solver.objective_value if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
    }

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        schedule = []
        for op in sorted(by_op):
            chosen = [m for (o, m), p in presences.items() if o == op and solver.boolean_value(p)]
            if len(chosen) != 1:
                raise RuntimeError(f"bad choice cardinality op={op}: {chosen}")
            m = chosen[0]
            duration = next(int(x["duration"]) for x in by_op[op] if int(x["machine"]) == m)
            schedule.append({
                "operation": op,
                "machine": m,
                "start": solver.value(starts[op]),
                "end": solver.value(ends[op]),
                "duration": duration,
            })
        result["certificate"] = schedule
        result["makespan"] = int(solver.value(makespan))
        result["improves_public_ub"] = result["makespan"] < published_ub
        result["closes_public_gap"] = result["makespan"] <= published_lb

    p = out / f"{a.instance}-seed{a.seed}-r2.json"
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result.get(k) for k in (
        "instance", "seed", "workers", "status", "published_lb", "published_ub",
        "target", "objective", "best_objective_bound", "solution_count", "wall_time_s",
        "improves_public_ub", "closes_public_gap")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
