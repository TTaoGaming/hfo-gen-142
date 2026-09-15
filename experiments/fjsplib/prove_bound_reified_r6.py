#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, platform, time, urllib.request
from collections import defaultdict
from pathlib import Path
from ortools.sat.python import cp_model
import ortools

PIN='7b3f6fb1384309bd4abca866fe3bef2993139b91'
ROOT=f'https://raw.githubusercontent.com/ScheduleOpt/benchmarks/{PIN}/flexible-jobshop'

def fetch(url):
    with urllib.request.urlopen(url,timeout=30) as r: raw=r.read()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--instance',required=True); ap.add_argument('--target',type=int,required=True); ap.add_argument('--seconds',type=float,default=900); ap.add_argument('--workers',type=int,default=4); ap.add_argument('--out',required=True); a=ap.parse_args()
    inst,inst_sha=fetch(f'{ROOT}/instances/json/{a.instance}.json'); bks,bks_sha=fetch(f'{ROOT}/solutions/bks.json'); row=next(x for x in bks if x['instance']==a.instance)
    by=defaultdict(list)
    for x in inst['operations']: by[int(x['operation'])].append(x)
    model=cp_model.CpModel(); start={}; end={}; machines=defaultdict(list); presence={}
    for op in sorted(by):
        start[op]=model.new_int_var(0,a.target,f'task_start_{op}'); end[op]=model.new_int_var(0,a.target,f'task_end_{op}'); choices=[]
        for idx,x in enumerate(by[op]):
            m,d=int(x['machine']),int(x['duration']); p=model.new_bool_var(f'p_{op}_{m}_{idx}')
            ms=model.new_int_var(0,a.target,f'mode_start_{op}_{m}_{idx}'); me=model.new_int_var(0,a.target,f'mode_end_{op}_{m}_{idx}')
            iv=model.new_optional_interval_var(ms,d,me,p,f'mode_iv_{op}_{m}_{idx}')
            model.add(start[op]==ms).only_enforce_if(p); model.add(end[op]==me).only_enforce_if(p)
            machines[m].append(iv); choices.append(p); presence[(op,m,idx)]=p
        model.add_exactly_one(choices)
    for e in inst['precedences']: model.add(end[int(e['before'])] <= start[int(e['after'])])
    for xs in machines.values(): model.add_no_overlap(xs)
    # No objective: SAT means counterexample <= target; INFEASIBLE proves the bound under this independent formulation.
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=a.seconds; solver.parameters.num_search_workers=a.workers; solver.parameters.log_search_progress=True
    t=time.monotonic(); status=solver.solve(model); elapsed=time.monotonic()-t; name=solver.status_name(status)
    payload={'schema':'hfo.fjsplib-reified-bound-proof.v1','instance':a.instance,'target':a.target,'source_commit':PIN,'instance_sha256':inst_sha,'bks_sha256':bks_sha,'published_lb':int(row['lower_bound']),'published_ub':int(row['upper_bound']),'operations':len(by),'modes':sum(len(v) for v in by.values()),'machines':len(machines),'precedences':len(inst['precedences']),'status':name,'wall_time_s':elapsed,'workers':a.workers,'ortools_version':ortools.__version__,'python':platform.python_version(),'proves_no_schedule_at_or_below_target':name=='INFEASIBLE'}
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        payload['counterexample_makespan']=max(solver.value(end[o]) for o in end)
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print(json.dumps(payload,sort_keys=True))
if __name__=='__main__': main()
