"""Shinka evaluator adapter: bounded literal genome -> SciPy -> frozen geometry."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse,ast,hashlib,json,time,subprocess
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from packing_generations import verify

def stop_mission(url):
    reply=subprocess.run(['curl','--fail','--silent','--show-error','--max-time','15','-X','POST',url],capture_output=True,text=True,check=True,timeout=20)
    if json.loads(reply.stdout).get('stopped') is not True:raise RuntimeError('STOP_ACK_MISSING')

def genome(text):
    if len(text)>8192:raise ValueError('GENOME_SIZE')
    g=ast.literal_eval(text)
    if not isinstance(g,dict) or set(g)!={'method','noise','beta','target_gain','maxiter','seed'}:raise ValueError('GENOME_SHAPE')
    if g['method'] not in ('shell','full'):raise ValueError('METHOD')
    for k,lo,hi in [('noise',0,0.02),('beta',100,1000000),('target_gain',1e-9,1e-3),('maxiter',1,500),('seed',0,2147483647)]:
        if type(g[k]) not in (int,float) or not np.isfinite(g[k]) or not lo<=g[k]<=hi:raise ValueError('GENOME_BOUND')
    if type(g['maxiter']) is not int or type(g['seed']) is not int:raise ValueError('GENOME_INTEGER')
    return g

def evaluate(program,output):
    root=Path(__file__).resolve().parent;output=Path(output);output.mkdir(exist_ok=True,parents=True)
    parent=(root/'parent.pck').read_bytes()
    if hashlib.sha256(parent).hexdigest()!='8ed8148be615d06c4bf37bf8fe5715248923486b93ab36d2d49b3d503b9da517':raise ValueError('PARENT_HASH')
    baseline=float(parent.splitlines()[0]);best=parent;best_score=baseline;history=[];start=time.monotonic()
    def record(x,label):
        nonlocal best,best_score
        i,j=np.triu_indices(119,1)
        r=min(1-np.linalg.norm(x,axis=1).max(),np.sqrt(np.sum((x[i]-x[j])**2,axis=1)).min()/2)-1e-10
        if not np.isfinite(r) or r<=0:return
        data=(f'{r:.16f}\nHenry Cohn spherical-code donor; Tommy Tai adaptation\n'+''.join(' '.join(f'{v:.16f}' for v in row)+'\n' for row in x)).encode()
        valid=False
        if r>best_score:
            try:verify(data);valid=True
            except ValueError:pass
            if valid:best,best_score=data,r
        history.append({'trial':label,'radius':r,'accepted_improvement':valid})
    try:
        g=genome(Path(program).read_text());verify(parent)
        original=np.array([[float(v) for v in s.split()] for s in parent.decode().splitlines()[2:]])
        rng=np.random.default_rng(g['seed'])
        for trial in range(8):
            if time.monotonic()-start>35:break
            if g['method']=='shell':
                u=original[1:]/np.linalg.norm(original[1:],axis=1)[:,None]
                x=u+rng.normal(size=u.shape)*g['noise'];i,j=np.triu_indices(118,1);beta=g['beta']
                def objective(z):
                    if time.monotonic()-start>40:raise TimeoutError()
                    x=z.reshape(118,6);norm=np.linalg.norm(x,axis=1);y=x/norm[:,None]
                    dots=np.sum(y[i]*y[j],axis=1);m=dots.max();w=np.exp(beta*(dots-m));total=w.sum();w/=total
                    grad=np.zeros_like(y);np.add.at(grad,i,w[:,None]*y[j]);np.add.at(grad,j,w[:,None]*y[i])
                    return m+np.log(total)/beta,((grad-y*np.sum(grad*y,axis=1)[:,None])/norm[:,None]).ravel()
                opt=minimize(objective,x.ravel(),jac=True,method='L-BFGS-B',options={'maxiter':g['maxiter'],'ftol':1e-15,'gtol':1e-11,'maxls':20})
                y=opt.x.reshape(118,6);y/=np.linalg.norm(y,axis=1)[:,None]
                d=np.sqrt(np.sum((y[i]-y[j])**2,axis=1)).min();r=min(d/(2+d),1/3)-1e-10
                record(np.vstack([np.zeros((1,6)),y*(1-r-1e-10)]),trial)
            else:
                x=original+rng.normal(size=original.shape)*g['noise'];i,j=np.triu_indices(119,1);r=baseline+g['target_gain']
                def objective(z):
                    if time.monotonic()-start>40:raise TimeoutError()
                    x=z.reshape(119,6);delta=x[i]-x[j]
                    pair=np.maximum(0,4*r*r-np.sum(delta*delta,axis=1));wall=np.maximum(0,np.sum(x*x,axis=1)-(1-r)**2)
                    grad=4*wall[:,None]*x;np.add.at(grad,i,-4*pair[:,None]*delta);np.add.at(grad,j,4*pair[:,None]*delta)
                    return np.sum(pair*pair)+np.sum(wall*wall),grad.ravel()
                opt=minimize(objective,x.ravel(),jac=True,method='L-BFGS-B',options={'maxiter':g['maxiter'],'ftol':1e-20,'gtol':1e-14,'maxls':20})
                record(opt.x.reshape(119,6),trial)
        reason='COMPLETE'
    except TimeoutError:reason='CPU_SLICE_EXHAUSTED'
    except (ValueError,SyntaxError,TypeError) as e:reason=type(e).__name__
    verification=verify(best);winner=best_score>baseline+1e-8
    (output/'accepted.pck').write_bytes(best)
    metrics={'combined_score':best_score,'public':{'radius':best_score,'baseline':baseline,'winner':winner,'trial_count':len(history),'reason':reason},'private':{'parent_sha256':hashlib.sha256(parent).hexdigest(),'accepted_sha256':hashlib.sha256(best).hexdigest(),'verification':verification,'history':history,'elapsed_seconds':time.monotonic()-start}}
    (output/'metrics.json').write_text(json.dumps(metrics));(output/'correct.json').write_text(json.dumps({'correct':reason in ('COMPLETE','CPU_SLICE_EXHAUSTED'),'error':None if history else reason}))
    if winner and os.environ.get('CELL_STOP_URL'):
        stop_mission(os.environ['CELL_STOP_URL'])
    print(json.dumps(metrics['public']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--program_path');p.add_argument('--results_dir');a=p.parse_args();evaluate(a.program_path,a.results_dir)
