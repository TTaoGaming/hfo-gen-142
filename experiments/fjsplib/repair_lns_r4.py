#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, random, time, urllib.request
from collections import defaultdict, deque
from pathlib import Path
from ortools.sat.python import cp_model

PIN="7b3f6fb1384309bd4abca866fe3bef2993139b91"
ROOT=f"https://raw.githubusercontent.com/ScheduleOpt/benchmarks/{PIN}/flexible-jobshop"

def fetch_json(url):
    with urllib.request.urlopen(url,timeout=30) as r: raw=r.read()
    return json.loads(raw),hashlib.sha256(raw).hexdigest()

def graph(inst):
    by=defaultdict(list); pred=defaultdict(list); succ=defaultdict(list)
    for x in inst['operations']: by[int(x['operation'])].append(x)
    for e in inst['precedences']:
        a,b=int(e['before']),int(e['after']); succ[a].append(b); pred[b].append(a)
    return by,pred,succ

def critical_neighborhood(cert,pred):
    c={int(x['operation']):x for x in cert}; bym=defaultdict(list)
    for x in cert: bym[int(x['machine'])].append(x)
    incoming=defaultdict(list)
    for op,x in c.items():
        for p in pred[op]:
            if int(c[p]['end'])==int(x['start']): incoming[op].append(p)
    for xs in bym.values():
        xs.sort(key=lambda z:(z['start'],z['end'],z['operation']))
        for a,b in zip(xs,xs[1:]):
            if int(a['end'])==int(b['start']): incoming[int(b['operation'])].append(int(a['operation']))
    makespan=max(int(x['end']) for x in cert); q=deque(int(x['operation']) for x in cert if int(x['end'])==makespan); crit=set(q)
    while q:
        u=q.popleft()
        for p in incoming[u]:
            if p not in crit: crit.add(p); q.append(p)
    return crit

def solve_target(inst,base,target,seed,seconds,workers,free_fraction):
    by,pred,succ=graph(inst); baseop={int(x['operation']):x for x in base}; crit=critical_neighborhood(base,pred)
    rng=random.Random(seed); free=set(crit)
    # expand around critical precedence and machine neighborhood
    for op in list(crit): free.update(pred[op]); free.update(succ[op])
    remaining=[o for o in by if o not in free]; rng.shuffle(remaining); free.update(remaining[:int(len(remaining)*free_fraction)])
    model=cp_model.CpModel(); starts={}; ends={}; pres={}; machines=defaultdict(list)
    for op in sorted(by):
        starts[op]=model.new_int_var(0,target,f's_{op}'); ends[op]=model.new_int_var(0,target,f'e_{op}'); ps=[]
        for x in by[op]:
            m,d=int(x['machine']),int(x['duration']); p=model.new_bool_var(f'op_{op}_m_{m}')
            machines[m].append(model.new_optional_interval_var(starts[op],d,ends[op],p,f'iv_{op}_m_{m}')); pres[(op,m)]=p; ps.append(p)
        model.add_exactly_one(ps)
    for e in inst['precedences']: model.add(ends[int(e['before'])] <= starts[int(e['after'])])
    for m in machines: model.add_no_overlap(machines[m])
    ms=model.new_int_var(0,target,'makespan'); model.add_max_equality(ms,[ends[o] for o in ends]); model.add(ms<=target)
    for op,x in baseop.items():
        model.add_hint(starts[op],min(int(x['start']),target)); model.add_hint(ends[op],min(int(x['end']),target))
        for (o,m),p in pres.items():
            if o!=op: continue
            want=1 if m==int(x['machine']) else 0; model.add_hint(p,want)
            if op not in free: model.add(p==want)
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=seconds; solver.parameters.num_search_workers=workers
    solver.parameters.random_seed=seed; solver.parameters.randomize_search=True; solver.parameters.log_search_progress=False
    t=time.monotonic(); status=solver.solve(model); elapsed=time.monotonic()-t
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE): return None,{'status':solver.status_name(status),'bound':solver.best_objective_bound,'free_ops':len(free),'critical_ops':len(crit),'seconds':elapsed}
    cert=[]
    for op in sorted(by):
        chosen=[m for (o,m),p in pres.items() if o==op and solver.boolean_value(p)]; m=chosen[0]
        d=next(int(x['duration']) for x in by[op] if int(x['machine'])==m)
        cert.append({'operation':op,'machine':m,'start':solver.value(starts[op]),'end':solver.value(ends[op]),'duration':d})
    return cert,{'status':solver.status_name(status),'makespan':solver.value(ms),'free_ops':len(free),'critical_ops':len(crit),'seconds':elapsed}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--incumbent',required=True); ap.add_argument('--target',type=int,required=True); ap.add_argument('--attempts',type=int,default=8)
    ap.add_argument('--seconds',type=float,default=60); ap.add_argument('--workers',type=int,default=8); ap.add_argument('--outdir',default='out-r4'); a=ap.parse_args()
    parent=json.loads(Path(a.incumbent).read_text()); name=parent['instance']; base=parent['certificate']
    inst,inst_sha=fetch_json(f"{ROOT}/instances/json/{name}.json"); bks,bks_sha=fetch_json(f"{ROOT}/solutions/bks.json"); row=next(x for x in bks if x['instance']==name)
    fractions=[0.05,0.10,0.20,0.35,0.50,0.70,0.90,1.00]; traces=[]; found=None
    for i in range(a.attempts):
        frac=fractions[i%len(fractions)]; cert,trace=solve_target(inst,base,a.target,7919+i*104729,a.seconds,a.workers,frac); trace['fraction']=frac; traces.append(trace)
        print(json.dumps({'attempt':i,**trace}),flush=True)
        if cert is not None: found=cert; break
    out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    result={'schema':'hfo.fjsplib-lns-repair.v1','instance':name,'source_commit':PIN,'instance_sha256':inst_sha,'bks_sha256':bks_sha,
            'parent_makespan':int(parent['makespan']),'target':a.target,'published_lb':int(row['lower_bound']),'published_ub':int(row['upper_bound']),'traces':traces,
            'status':'FEASIBLE' if found else 'NO_CERTIFICATE'}
    if found:
        result['certificate']=found; result['makespan']=max(int(x['end']) for x in found); result['improves_public_ub']=result['makespan']<int(row['upper_bound']); result['closes_public_gap']=result['makespan']<=int(row['lower_bound'])
    p=out/f"{name}-target{a.target}-r4.json"; p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n'); print(json.dumps({k:result.get(k) for k in ('instance','status','parent_makespan','target','makespan','improves_public_ub','closes_public_gap')}))
    return 0
if __name__=='__main__': raise SystemExit(main())
