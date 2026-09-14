import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import json,time,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
p=Path(__file__).resolve().parent
raw=(p/'parent.pck').read_bytes()
# Input and kernel hashes are checked by the frozen generation driver.
rows=np.array([[float(x) for x in s.split()] for s in raw.decode().splitlines()[2:]])
assert rows.shape==(119,6) and np.linalg.norm(rows[0])==0
u=rows[1:]/np.linalg.norm(rows[1:],axis=1)[:,None]
i,j=np.triu_indices(118,1);start=time.monotonic();best=float(raw.splitlines()[0]);history=[]
def emit(v,label):
 global best
 v=v/np.linalg.norm(v,axis=1)[:,None]
 d=np.sqrt(np.min(np.sum((v[i]-v[j])**2,axis=1)))
 r=min(d/(2+d),1/3)-1e-10
 history.append({'label':label,'radius':r,'elapsed':time.monotonic()-start})
 if r>best:
  centers=np.vstack([np.zeros((1,6)),v*(1-r-1e-10)])
  text=f'{r:.16f}\nHenry Cohn (spherical-code donor), Tommy Tai (packing adaptation; AI-assisted)\n'+''.join(' '.join(f'{x:.16f}' for x in a)+'\n' for a in centers)
  (p/'best.pck').write_text(text);best=r
 (p/'search.json').write_text(json.dumps({'history':history,'best_radius':best,'provider_calls':0,'retries':0,'elapsed':time.monotonic()-start,'method':'spherical-shell multistart smooth minimax; fixed origin'},indent=2))
emit(u,'normalized_parent')
import sys
rng=np.random.default_rng(914119+int(sys.argv[1]))
for restart,noise in enumerate([0,1e-5,1e-3,0.01]):
 v=u+rng.normal(size=u.shape)*noise
 for beta in [100,1000,10000]:
  def objective(flat):
   if time.monotonic()-start>90:raise TimeoutError('90s budget')
   x=flat.reshape(118,6);norm=np.linalg.norm(x,axis=1);y=x/norm[:,None]
   dots=np.sum(y[i]*y[j],axis=1);m=dots.max();w=np.exp(beta*(dots-m));w/=w.sum()
   g=np.zeros_like(y);np.add.at(g,i,w[:,None]*y[j]);np.add.at(g,j,w[:,None]*y[i])
   g=(g-y*np.sum(g*y,axis=1)[:,None])/norm[:,None]
   return m+np.log(np.exp(beta*(dots-m)).sum())/beta,g.ravel()
  try:
   opt=minimize(objective,v.ravel(),jac=True,method='L-BFGS-B',options={'maxiter':500,'ftol':1e-14,'gtol':1e-10,'maxls':20})
  except TimeoutError:raise SystemExit(0)
  v=opt.x.reshape(118,6);emit(v,f'restart{restart}_beta{beta}')
print(json.dumps({'best_radius':best,'elapsed':time.monotonic()-start,'attempts':len(history),'provider_calls':0}))
