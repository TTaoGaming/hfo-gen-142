#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, math, random, time, urllib.request
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
    by_op = defaultdict(list); pred = defaultdict(list); succ = defaultdict(list)
    for x in inst["operations"]: by_op[int(x["operation"])].append(x)
    for e in inst["precedences"]:
        b, a = int(e["before"]), int(e["after"]); succ[b].append(a); pred[a].append(b)
    return by_op, pred, succ


def critical_tail(by_op, succ):
    memo = {}
    def rec(op):
        if op in memo: return memo[op]
        own = min(int(x["duration"]) for x in by_op[op])
        memo[op] = own + max((rec(v) for v in succ[op]), default=0)
        return memo[op]
    for op in by_op: rec(op)
    return memo


def constructive(inst, seed: int, variant: int):
    """Create an always-feasible append-only schedule.

    This is a donor/hint generator, never the verifier or crown metric.
    Variants change only priority weights/tie breaks for cheap diversity.
    """
    by_op, pred, succ = build_graph(inst); tails = critical_tail(by_op, succ)
    rng = random.Random((seed + 1) * 1_000_003 + variant * 97)
    scheduled = {}; machine_free = defaultdict(int); ready = {o for o in by_op if not pred[o]}
    tw = rng.uniform(0.7, 2.8); fw = rng.uniform(0.15, 1.2); rw = rng.uniform(0.0, 0.8)
    while ready:
        choices = []
        for op in ready:
            release = max((scheduled[p]["end"] for p in pred[op]), default=0)
            machine_opts = []
            for x in by_op[op]:
                m, d = int(x["machine"]), int(x["duration"])
                s = max(release, machine_free[m]); e = s + d
                machine_opts.append((e + rng.random() * 0.01, e, s, m, d))
            _, e, s, m, d = min(machine_opts)
            # Critical-tail pressure competes with immediate completion/load pressure.
            score = tw * tails[op] - fw * e - rw * machine_free[m] + rng.random() * 2.0
            choices.append((-score, e, op, m, s, d))
        _, e, op, m, s, d = min(choices)
        ready.remove(op)
        scheduled[op] = {"operation": op, "machine": m, "start": s, "end": e, "duration": d}
        machine_free[m] = e
        for nxt in succ[op]:
            if nxt not in scheduled and all(p in scheduled for p in pred[nxt]): ready.add(nxt)
    if len(scheduled) != len(by_op): raise RuntimeError("constructive schedule did not cover DAG")
    return max(x["end"] for x in scheduled.values()), [scheduled[o] for o in sorted(scheduled)]


def best_constructive(inst, seed: int, count: int):
    best = None
    for v in range(count):
        ms, cert = constructive(inst, seed, v)
        if best is None or ms < best[0]: best = (ms, cert, v)
    return best


class TargetStopper(cp_model.CpSolverSolutionCallback):
    def __init__(self, target: int): super().__init__(); self.target = target; self.best = None; self.hits = 0
    def on_solution_callback(self):
        value = int(round(self.objective_value)); self.hits += 1
        self.best = value if self.best is None else min(self.best, value)
        if value <= self.target: self.stop_search()


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--instance',required=True); ap.add_argument('--seed',type=int,required=True)
    ap.add_argument('--seconds',type=float,default=600); ap.add_argument('--workers',type=int,default=8)
    ap.add_argument('--constructs',type=int,default=128); ap.add_argument('--outdir',default='out'); ap.add_argument('--heuristic-only',action='store_true')
    a=ap.parse_args()
    inst, inst_sha = fetch_json(f"{ROOT}/instances/json/{a.instance}.json"); bks,bks_sha=fetch_json(f"{ROOT}/solutions/bks.json")
    row=next(x for x in bks if x['instance']==a.instance); pub_ub=int(row['upper_bound']); pub_lb=int(row['lower_bound']); target=pub_ub-1
    h_ms,h_cert,h_variant=best_constructive(inst,a.seed,a.constructs)
    out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    if a.heuristic_only:
        print(json.dumps({'instance':a.instance,'heuristic_makespan':h_ms,'published_lb':pub_lb,'published_ub':pub_ub,'variant':h_variant}))
        return 0

    by_op,pred,succ=build_graph(inst); horizon=max(h_ms,pub_ub); machines=defaultdict(list)
    model=cp_model.CpModel(); starts={}; ends={}; pres={}
    for op in sorted(by_op):
        starts[op]=model.new_int_var(0,horizon,f's_{op}'); ends[op]=model.new_int_var(0,horizon,f'e_{op}'); ps=[]
        for x in by_op[op]:
            m,d=int(x['machine']),int(x['duration']); p=model.new_bool_var(f'op_{op}_m_{m}')
            machines[m].append(model.new_optional_interval_var(starts[op],d,ends[op],p,f'iv_{op}_m_{m}')); pres[(op,m)]=p; ps.append(p)
        model.add_exactly_one(ps)
    for e in inst['precedences']: model.add(ends[int(e['before'])] <= starts[int(e['after'])])
    for m in machines: model.add_no_overlap(machines[m])
    makespan=model.new_int_var(0,horizon,'makespan'); model.add_max_equality(makespan,[ends[o] for o in sorted(ends)]); model.minimize(makespan)

    hint={x['operation']:x for x in h_cert}
    for op,x in hint.items():
        model.add_hint(starts[op],x['start']); model.add_hint(ends[op],x['end'])
        for (o,m),p in pres.items():
            if o==op: model.add_hint(p,1 if m==x['machine'] else 0)
    model.add_hint(makespan,h_ms)

    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=a.seconds; solver.parameters.num_search_workers=a.workers
    solver.parameters.random_seed=a.seed; solver.parameters.randomize_search=True; solver.parameters.log_search_progress=True
    cb=TargetStopper(target); t=time.monotonic(); status=solver.solve(model,cb); elapsed=time.monotonic()-t; sn=solver.status_name(status)
    result={'schema':'hfo.fjsplib-bks-hunt.v3','instance':a.instance,'source_commit':PIN,'instance_sha256':inst_sha,'bks_sha256':bks_sha,
            'published_lb':pub_lb,'published_ub':pub_ub,'target':target,'seed':a.seed,'workers':a.workers,'constructs':a.constructs,
            'constructive_makespan':h_ms,'constructive_variant':h_variant,'search_horizon':horizon,'status':sn,'wall_time_s':elapsed,
            'solution_count':cb.hits,'best_objective_bound':solver.best_objective_bound if status in (cp_model.OPTIMAL,cp_model.FEASIBLE,cp_model.UNKNOWN) else None,
            'objective':solver.objective_value if status in (cp_model.OPTIMAL,cp_model.FEASIBLE) else None}
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        cert=[]
        for op in sorted(by_op):
            chosen=[m for (o,m),p in pres.items() if o==op and solver.boolean_value(p)]; m=chosen[0]
            d=next(int(x['duration']) for x in by_op[op] if int(x['machine'])==m)
            cert.append({'operation':op,'machine':m,'start':solver.value(starts[op]),'end':solver.value(ends[op]),'duration':d})
        result['certificate']=cert; result['makespan']=int(solver.value(makespan)); result['improves_public_ub']=result['makespan']<pub_ub; result['closes_public_gap']=result['makespan']<=pub_lb
    p=out/f"{a.instance}-seed{a.seed}-r3.json"; p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result.get(k) for k in ['instance','seed','status','published_lb','published_ub','constructive_makespan','objective','best_objective_bound','solution_count','wall_time_s','improves_public_ub','closes_public_gap']},sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
