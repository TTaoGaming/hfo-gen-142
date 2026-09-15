#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
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


def build_graph(inst):
    by_op = defaultdict(list)
    pred = defaultdict(list)
    succ = defaultdict(list)
    for x in inst["operations"]:
        by_op[int(x["operation"])].append(x)
    for e in inst["precedences"]:
        before, after = int(e["before"]), int(e["after"])
        succ[before].append(after)
        pred[after].append(before)
    return by_op, pred, succ


def critical_tail(by_op, succ):
    memo = {}

    def rec(op):
        if op in memo:
            return memo[op]
        own = min(int(x["duration"]) for x in by_op[op])
        memo[op] = own + max((rec(v) for v in succ[op]), default=0)
        return memo[op]

    for op in by_op:
        rec(op)
    return memo


def earliest_gap(timeline, release: int, duration: int) -> int:
    """Earliest legal start in a sorted machine timeline.

    R3 was append-only (machine_free). R4 explicitly reuses interior idle gaps,
    which is the sole intended phenotype mutation in this descendant.
    """
    t = release
    for start, end, _op in timeline:
        if t + duration <= start:
            return t
        if end > t:
            t = end
    return t


def constructive(inst, seed: int, variant: int):
    by_op, pred, succ = build_graph(inst)
    tails = critical_tail(by_op, succ)
    rng = random.Random((seed + 1) * 1_000_003 + variant * 97)
    scheduled = {}
    machine_timeline = defaultdict(list)
    ready = {op for op in by_op if not pred[op]}

    tail_weight = rng.uniform(0.5, 3.5)
    finish_weight = rng.uniform(0.05, 1.5)
    start_weight = rng.uniform(0.0, 1.5)
    load_weight = rng.uniform(0.0, 1.0)

    while ready:
        choices = []
        for op in ready:
            release = max((scheduled[p]["end"] for p in pred[op]), default=0)
            machine_choices = []
            for x in by_op[op]:
                machine = int(x["machine"])
                duration = int(x["duration"])
                start = earliest_gap(machine_timeline[machine], release, duration)
                end = start + duration
                load = sum(b - a for a, b, _ in machine_timeline[machine])
                local_score = (
                    end
                    + start_weight * start
                    + load_weight * load
                    + rng.random() * 0.05
                )
                machine_choices.append((local_score, end, start, machine, duration))

            _, end, start, machine, duration = min(machine_choices)
            priority = (
                tail_weight * tails[op]
                - finish_weight * end
                - rng.uniform(0.0, 2.0)
            )
            choices.append((-priority, end, op, machine, start, duration))

        _, end, op, machine, start, duration = min(choices)
        ready.remove(op)
        scheduled[op] = {
            "operation": op,
            "machine": machine,
            "start": start,
            "end": end,
            "duration": duration,
        }
        bisect.insort(machine_timeline[machine], (start, end, op))
        for nxt in succ[op]:
            if nxt not in scheduled and all(p in scheduled for p in pred[nxt]):
                ready.add(nxt)

    if len(scheduled) != len(by_op):
        raise RuntimeError("constructive schedule did not cover DAG")
    return max(x["end"] for x in scheduled.values()), [scheduled[o] for o in sorted(scheduled)]


def best_constructive(inst, seed: int, count: int):
    best = None
    for variant in range(count):
        makespan, cert = constructive(inst, seed, variant)
        if best is None or makespan < best[0]:
            best = (makespan, cert, variant)
    return best


class TargetStopper(cp_model.CpSolverSolutionCallback):
    def __init__(self, target: int):
        super().__init__()
        self.target = target
        self.best = None
        self.hits = 0

    def on_solution_callback(self):
        value = int(round(self.objective_value))
        self.hits += 1
        self.best = value if self.best is None else min(self.best, value)
        if value <= self.target:
            self.stop_search()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--instance", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--seconds", type=float, default=180)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--constructs", type=int, default=1200)
    ap.add_argument("--outdir", default="out")
    args = ap.parse_args()

    inst, inst_sha = fetch_json(f"{ROOT}/instances/json/{args.instance}.json")
    bks, bks_sha = fetch_json(f"{ROOT}/solutions/bks.json")
    row = next(x for x in bks if x["instance"] == args.instance)
    pub_ub = int(row["upper_bound"])
    pub_lb = int(row["lower_bound"])
    target = pub_ub - 1

    c0 = time.monotonic()
    h_ms, h_cert, h_variant = best_constructive(inst, args.seed, args.constructs)
    constructive_s = time.monotonic() - c0

    by_op, pred, succ = build_graph(inst)
    horizon = max(h_ms, pub_ub)
    model = cp_model.CpModel()
    starts, ends, pres = {}, {}, {}
    machine_intervals = defaultdict(list)

    for op in sorted(by_op):
        starts[op] = model.new_int_var(0, horizon, f"s_{op}")
        ends[op] = model.new_int_var(0, horizon, f"e_{op}")
        choices = []
        for x in by_op[op]:
            machine, duration = int(x["machine"]), int(x["duration"])
            p = model.new_bool_var(f"op_{op}_m_{machine}")
            iv = model.new_optional_interval_var(
                starts[op], duration, ends[op], p, f"iv_{op}_m_{machine}"
            )
            machine_intervals[machine].append(iv)
            pres[(op, machine)] = p
            choices.append(p)
        model.add_exactly_one(choices)

    for e in inst["precedences"]:
        model.add(ends[int(e["before"])] <= starts[int(e["after"])])
    for machine in machine_intervals:
        model.add_no_overlap(machine_intervals[machine])

    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [ends[o] for o in sorted(ends)])
    model.minimize(makespan)

    hint = {x["operation"]: x for x in h_cert}
    for op, x in hint.items():
        model.add_hint(starts[op], x["start"])
        model.add_hint(ends[op], x["end"])
        for (candidate_op, machine), p in pres.items():
            if candidate_op == op:
                model.add_hint(p, 1 if machine == x["machine"] else 0)
    model.add_hint(makespan, h_ms)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed
    solver.parameters.randomize_search = True
    solver.parameters.log_search_progress = True
    callback = TargetStopper(target)

    t0 = time.monotonic()
    status = solver.solve(model, callback)
    elapsed = time.monotonic() - t0
    status_name = solver.status_name(status)

    result = {
        "schema": "hfo.fjsplib-bks-hunt.v4-gap-insertion",
        "instance": args.instance,
        "source_commit": PIN,
        "instance_sha256": inst_sha,
        "bks_sha256": bks_sha,
        "published_lb": pub_lb,
        "published_ub": pub_ub,
        "target": target,
        "seed": args.seed,
        "workers": args.workers,
        "constructs": args.constructs,
        "constructive_makespan": h_ms,
        "constructive_variant": h_variant,
        "constructive_wall_time_s": constructive_s,
        "search_horizon": horizon,
        "status": status_name,
        "wall_time_s": elapsed,
        "solution_count": callback.hits,
        "best_objective_bound": solver.best_objective_bound if status in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.UNKNOWN) else None,
        "objective": solver.objective_value if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
    }

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        cert = []
        for op in sorted(by_op):
            chosen = [m for (o, m), p in pres.items() if o == op and solver.boolean_value(p)]
            machine = chosen[0]
            duration = next(int(x["duration"]) for x in by_op[op] if int(x["machine"]) == machine)
            cert.append({
                "operation": op,
                "machine": machine,
                "start": solver.value(starts[op]),
                "end": solver.value(ends[op]),
                "duration": duration,
            })
        result["certificate"] = cert
        result["makespan"] = int(solver.value(makespan))
        result["improves_public_ub"] = result["makespan"] < pub_ub
        result["closes_public_gap"] = result["makespan"] <= pub_lb

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{args.instance}-seed{args.seed}-r4-gap.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        k: result.get(k)
        for k in [
            "instance", "seed", "published_lb", "published_ub",
            "constructive_makespan", "constructive_wall_time_s",
            "status", "objective", "best_objective_bound", "solution_count",
            "wall_time_s", "improves_public_ub", "closes_public_gap",
        ]
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
