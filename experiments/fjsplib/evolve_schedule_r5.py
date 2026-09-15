#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, random, urllib.request
from collections import defaultdict, deque
from pathlib import Path

PIN='7b3f6fb1384309bd4abca866fe3bef2993139b91'
ROOT=f'https://raw.githubusercontent.com/ScheduleOpt/benchmarks/{PIN}/flexible-jobshop'

def fetch_json(url):
    with urllib.request.urlopen(url,timeout=30) as r: raw=r.read()
    return json.loads(raw),hashlib.sha256(raw).hexdigest()

def load_problem(inst):
    alts=defaultdict(dict); preds=defaultdict(list)
    for x in inst['operations']: alts[int(x['operation'])][int(x['machine'])]=int(x['duration'])
    for e in inst['precedences']: preds[int(e['after'])].append(int(e['before']))
    return alts,preds

def from_certificate(cert):
    assign={int(x['operation']):int(x['machine']) for x in cert}; seq=defaultdict(list)
    for x in sorted(cert,key=lambda z:(int(z['machine']),int(z['start']),int(z['end']),int(z['operation']))): seq[int(x['machine'])].append(int(x['operation']))
    return assign,{m:list(xs) for m,xs in seq.items()}

def evaluate(alts,preds,assign,seq):
    nodes=sorted(alts); succ=defaultdict(list); indeg={o:0 for o in nodes}
    for o in nodes:
        for p in preds[o]: succ[p].append(o); indeg[o]+=1
    machine_prev={}
    for m,xs in seq.items():
        for a,b in zip(xs,xs[1:]): succ[a].append(b); indeg[b]+=1; machine_prev[b]=a
    q=deque(sorted(o for o in nodes if indeg[o]==0)); start={}; end={}; topo=[]
    while q:
        o=q.popleft(); topo.append(o); s=max((end[p] for p in preds[o]),default=0)
        if o in machine_prev: s=max(s,end[machine_prev[o]])
        d=alts[o][assign[o]]; start[o]=s; end[o]=s+d
        for v in succ[o]:
            indeg[v]-=1
            if indeg[v]==0: q.append(v)
    if len(topo)!=len(nodes): return None
    ms=max(end.values()); tight=defaultdict(list)
    for o in nodes:
        for p in preds[o]:
            if end[p]==start[o]: tight[o].append(p)
        if o in machine_prev and end[machine_prev[o]]==start[o]: tight[o].append(machine_prev[o])
    crit=set(); qq=deque(o for o in nodes if end[o]==ms); crit.update(qq)
    while qq:
        o=qq.popleft()
        for p in tight[o]:
            if p not in crit: crit.add(p); qq.append(p)
    cert=[{'operation':o,'machine':assign[o],'start':start[o],'end':end[o],'duration':alts[o][assign[o]]} for o in nodes]
    return ms,cert,crit

def mutate(alts,assign,seq,crit,rng):
    a=dict(assign); s={m:list(xs) for m,xs in seq.items()}; nodes=list(alts)
    o=rng.choice(list(crit) if crit and rng.random()<0.82 else nodes); old=a[o]
    options=list(alts[o]); new=rng.choice(options)
    oldseq=s.get(old,[]); oldseq.remove(o); s[old]=oldseq
    target=s.setdefault(new,[]); pos=rng.randrange(len(target)+1); target.insert(pos,o); a[o]=new
    return a,s

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--parent',required=True); ap.add_argument('--iterations',type=int,default=250000); ap.add_argument('--seed',type=int,default=1); ap.add_argument('--outdir',default='out-r5'); a=ap.parse_args()
    parent=json.loads(Path(a.parent).read_text()); name=parent['instance']; inst,inst_sha=fetch_json(f'{ROOT}/instances/json/{name}.json'); bks,bks_sha=fetch_json(f'{ROOT}/solutions/bks.json'); row=next(x for x in bks if x['instance']==name)
    alts,preds=load_problem(inst); assign,seq=from_certificate(parent['certificate']); ev=evaluate(alts,preds,assign,seq)
    if ev is None: raise SystemExit('PARENT_CYCLIC'); cur_ms,cur_cert,cur_crit=ev; best=(cur_ms,dict(assign),{m:list(v) for m,v in seq.items()},cur_cert)
    rng=random.Random(a.seed); accepted=0; feasible=0
    for it in range(a.iterations):
        na,ns=mutate(alts,assign,seq,cur_crit,rng); nev=evaluate(alts,preds,na,ns)
        if nev is None: continue
        feasible+=1; nms,ncert,ncrit=nev; temp=max(0.15,5.0*(1-it/max(1,a.iterations)))
        if nms<=cur_ms or rng.random()<math.exp(-(nms-cur_ms)/temp): assign,seq,cur_ms,cur_cert,cur_crit=na,ns,nms,ncert,ncrit; accepted+=1
        if nms<best[0]:
            best=(nms,dict(na),{m:list(v) for m,v in ns.items()},ncert); print(json.dumps({'iteration':it,'best':nms,'public_ub':row['upper_bound']}),flush=True)
            if nms<=int(row['lower_bound']): break
    ms,ba,bs,cert=best; out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    result={'schema':'hfo.fjsplib-memetic-r5.v1','instance':name,'source_commit':PIN,'instance_sha256':inst_sha,'bks_sha256':bks_sha,'parent_makespan':int(parent['makespan']),'makespan':ms,'published_lb':int(row['lower_bound']),'published_ub':int(row['upper_bound']),'iterations_budget':a.iterations,'feasible_children':feasible,'accepted_children':accepted,'seed':a.seed,'certificate':cert,'improves_public_ub':ms<int(row['upper_bound']),'closes_public_gap':ms<=int(row['lower_bound'])}
    p=out/f'{name}-seed{a.seed}-r5.json'; p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n'); print(json.dumps({k:result[k] for k in ('instance','seed','parent_makespan','makespan','published_lb','published_ub','feasible_children','accepted_children','improves_public_ub','closes_public_gap')},sort_keys=True))
if __name__=='__main__': main()
