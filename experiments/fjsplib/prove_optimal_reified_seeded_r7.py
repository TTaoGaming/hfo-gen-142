#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, platform, time, urllib.request
from collections import defaultdict
from pathlib import Path
import ortools
from ortools.sat.python import cp_model

PIN='7b3f6fb1384309bd4abca866fe3bef2993139b91'
ROOT=f'https://raw.githubusercontent.com/ScheduleOpt/benchmarks/{PIN}/flexible-jobshop'

def fetch(url):
    with urllib.request.urlopen(url,timeout=30) as r: raw=r.read()
    return json.loads(raw),hashlib.sha256(raw).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--instance',required=True); ap.add_argument('--certificate',required=True); ap.add_argument('--seconds',type=float,default=900); ap.add_argument('--workers',type=int,default=4); ap.add_argument('--out',required=True); a=ap.parse_args()
    inst,inst_sha=fetch(f'{ROOT}/instances/json/{a.instance}.json'); bks,bks_sha=fetch(f'{ROOT}/solutions/bks.json'); row=next(x for x in bks if x['instance']==a.instance)
    prod=json.loads(Path(a.certificate).read_text()); cert={int(x['operation']):x for x in prod['certificate']}; known=int(prod['makespan'])
    by=defaultdict(list)
    for x in inst['operations']: by[int(x['operation'])].append(x)
    model=cp_model.CpModel(); start={}; end={}; modes=defaultdict(list); presence={}; mode_start={}; mode_end={}
    for op in sorted(by):
        start[op]=model.new_int_var(0,known,f'task_start_{op}'); end[op]=model.new_int_var(0,known,f'task_end_{op}'); choices=[]
        for idx,x in enumerate(by[op]):
            m,d=int(x['machine']),int(x['duration']); key=(op,m,idx); p=model.new_bool_var(f'p_{op}_{m}_{idx}'); ms=model.new_int_var(0,known,f'mode_start_{op}_{m}_{idx}'); me=model.new_int_var(0,known,f'mode_end_{op}_{m}_{idx}')
            iv=model.new_optional_interval_var(ms,d,me,p,f'mode_iv_{op}_{m}_{idx}'); model.add(start[op]==ms).only_enforce_if(p); model.add(end[op]==me).only_enforce_if(p)
            modes[m].append(iv); presence[key]=p; mode_start[key]=ms; mode_end[key]=me; choices.append(p)
        model.add_exactly_one(choices)
    for e in inst['precedences']: model.add(end[int(e['before'])] <= start[int(e['after'])])
    for xs in modes.values(): model.add_no_overlap(xs)
    makespan=model.new_int_var(0,known,'makespan'); model.add_max_equality(makespan,[end[o] for o in sorted(end)]); model.minimize(makespan)
    for op,x in cert.items():
        chosen=int(x['machine']); s=int(x['start']); e=int(x['end']); model.add_hint(start[op],s); model.add_hint(end[op],e)
        for key,p in presence.items():
            o,m,_=key
            if o!=op: continue
            bit=1 if m==chosen else 0; model.add_hint(p,bit)
            if bit: model.add_hint(mode_start[key],s); model.add_hint(mode_end[key],e)
    model.add_hint(makespan,known)
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=a.seconds; solver.parameters.num_search_workers=a.workers; solver.parameters.log_search_progress=True
    t=time.monotonic(); status=solver.solve(model); elapsed=time.monotonic()-t; sn=solver.status_name(status)
    payload={'schema':'hfo.fjsplib-reified-seeded-opt-proof.v1','instance':a.instance,'source_commit':PIN,'instance_sha256':inst_sha,'bks_sha256':bks_sha,'published_lb':int(row['lower_bound']),'published_ub':int(row['upper_bound']),'known_feasible':known,'status':sn,'objective':solver.objective_value if status in (cp_model.OPTIMAL,cp_model.FEASIBLE) else None,'best_objective_bound':solver.best_objective_bound if status in (cp_model.OPTIMAL,cp_model.FEASIBLE,cp_model.UNKNOWN) else None,'wall_time_s':elapsed,'workers':a.workers,'ortools_version':ortools.__version__,'python':platform.python_version()}
    payload['proves_optimum_125']=sn=='OPTIMAL' and int(round(payload['objective']))==125 and int(round(payload['best_objective_bound']))==125
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print(json.dumps(payload,sort_keys=True))
if __name__=='__main__': main()
