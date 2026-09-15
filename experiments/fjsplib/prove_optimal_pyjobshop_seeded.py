#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, platform, time, urllib.request
from collections import defaultdict
from pathlib import Path

PIN='7b3f6fb1384309bd4abca866fe3bef2993139b91'
ROOT=f'https://raw.githubusercontent.com/ScheduleOpt/benchmarks/{PIN}/flexible-jobshop'

def fetch(url):
    with urllib.request.urlopen(url,timeout=30) as r: raw=r.read()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--instance',required=True); ap.add_argument('--certificate',required=True); ap.add_argument('--seconds',type=float,default=900); ap.add_argument('--workers',type=int,default=4); ap.add_argument('--out',required=True); a=ap.parse_args()
    import ortools, pyjobshop
    from pyjobshop import Model, ScheduledTask, Solution
    inst,inst_sha=fetch(f'{ROOT}/instances/json/{a.instance}.json'); bks,bks_sha=fetch(f'{ROOT}/solutions/bks.json'); row=next(x for x in bks if x['instance']==a.instance)
    producer=json.loads(Path(a.certificate).read_text()); cert={int(x['operation']):x for x in producer['certificate']}
    model=Model(); machine_ids=sorted({int(x['machine']) for x in inst['operations']}); machine_index={mid:i for i,mid in enumerate(machine_ids)}; machines={mid:model.add_machine(name=str(mid)) for mid in machine_ids}
    op_ids=sorted({int(x['operation']) for x in inst['operations']}); tasks={op:model.add_task(name=str(op)) for op in op_ids}; mode_index={}; mode_count=0
    for x in inst['operations']:
        op,mid,d=int(x['operation']),int(x['machine']),int(x['duration']); model.add_mode(tasks[op],machines[mid],duration=d); mode_index[(op,mid)]=mode_count; mode_count+=1
    for e in inst['precedences']: model.add_end_before_start(tasks[int(e['before'])],tasks[int(e['after'])])
    model.set_objective(weight_makespan=1)
    initial=[]
    for op in op_ids:
        x=cert[op]; mid=int(x['machine']); initial.append(ScheduledTask(mode=mode_index[(op,mid)],resources=[machine_index[mid]],start=int(x['start']),end=int(x['end'])))
    initial_solution=Solution(model.data(),initial)
    t=time.monotonic(); result=model.solve(time_limit=a.seconds,display=True,num_workers=a.workers,initial_solution=initial_solution); elapsed=time.monotonic()-t
    status=str(result.status); payload={'schema':'hfo.fjsplib-pyjobshop-seeded-opt-proof.v1','instance':a.instance,'source_commit':PIN,'instance_sha256':inst_sha,'bks_sha256':bks_sha,'published_lb':int(row['lower_bound']),'published_ub':int(row['upper_bound']),'initial_makespan':initial_solution.makespan,'status':status,'objective':None if result.objective==float('inf') else float(result.objective),'lower_bound':float(result.lower_bound),'runtime':float(result.runtime),'wall_time_s':elapsed,'workers':a.workers,'pyjobshop_version':getattr(pyjobshop,'__version__','unknown'),'ortools_version':ortools.__version__,'python':platform.python_version()}
    payload['proves_optimum_125']=('Optimal' in status and int(round(payload['objective']))==125 and int(round(payload['lower_bound']))==125)
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print(json.dumps(payload,sort_keys=True))
if __name__=='__main__': main()
