"""Zero-provider accepted-proposal recovery and separate exact verification."""
import hashlib,json,os,signal,sqlite3,subprocess,sys,threading,time,shutil
from fractions import Fraction
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import psutil

p=Path(sys.argv[1]).resolve();os.chdir(p);started=time.monotonic()
cached=json.loads((p/'cached-response.json').read_text());calls=[]
class Fixture(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
        if self.path.endswith('/stop'):value={'stopped':True}
        else:calls.append(hashlib.sha256(raw).hexdigest());value=cached
        data=json.dumps(value).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers()
        self.wfile.write(data)
server=ThreadingHTTPServer(('127.0.0.1',0),Fixture);threading.Thread(target=server.serve_forever,daemon=True).start()
env=dict(os.environ,SHINKA_EVAL_CHECKPOINT='1',CELL_API_URL=f'http://127.0.0.1:{server.server_port}/v1',CELL_STOP_URL=f'http://127.0.0.1:{server.server_port}/stop')
children=[]
def launch(label):
    stream=(p/f'{label}.log').open('w')
    child=subprocess.Popen([sys.executable,'run.py'],env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    children.append((child,stream));return child
def kill_tree(child):
    try:
        descendants=psutil.Process(child.pid).children(recursive=True)
        for node in descendants:
            try:node.kill()
            except psutil.NoSuchProcess:pass
        psutil.wait_procs(descendants,timeout=5)
    except psutil.NoSuchProcess:pass
    if child.poll() is None:os.killpg(child.pid,signal.SIGKILL)
    child.wait(timeout=10)
def archive():
    with sqlite3.connect('file:results/programs.sqlite?mode=ro',uri=True) as db:
        return db.execute('select id,generation from programs order by generation,id').fetchall()
def independent_verify(path):
    raw=path.read_bytes();lines=raw.decode().splitlines();radius=Fraction(lines[0]);points=[[Fraction(x) for x in s.split()] for s in lines[2:]]
    assert len(points)==119 and all(len(x)==6 for x in points) and 0<radius<1
    assert all(sum(x*x for x in a)<=(1-radius)**2 for a in points)
    pairs=0
    for i,a in enumerate(points):
        for b in points[:i]:
            assert sum((x-y)**2 for x,y in zip(a,b))>=4*radius**2;pairs+=1
    return {'sha256':hashlib.sha256(raw).hexdigest(),'radius':str(radius),'containment_checks':len(points),'pair_checks':pairs}
try:
    first=launch('caller-a');checkpoint=p/'results/gen_1/accepted-proposal.json'
    limit=time.monotonic()+65
    while not checkpoint.exists() and first.poll() is None and time.monotonic()<limit:time.sleep(.02)
    assert checkpoint.exists(),'NO_ACCEPTED_CHECKPOINT'
    before=archive();assert [x[1] for x in before]==[0],before
    kill_tree(first);before_calls=len(calls);assert before_calls==1
    import fcntl
    with (p/'.shinka-cell.lock').open('a') as held_lock:
        fcntl.flock(held_lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
        contender=subprocess.run([sys.executable,'run.py'],env=env,capture_output=True,text=True,timeout=10)
        assert contender.returncode!=0 and 'BlockingIOError' in contender.stderr
    negative={}
    for case in ('missing-checkpoint','changed-candidate','changed-evaluator'):
        work=p/case;work.mkdir()
        for name in ('run.py','evaluate.py','packing_generations.py','parent.pck','initial.py'):
            shutil.copy2(p/name,work/name)
        shutil.copytree(p/'results',work/'results')
        if case=='missing-checkpoint':(work/'results/gen_1/accepted-proposal.json').unlink()
        else:
            target=work/('results/gen_1/main.py' if case=='changed-candidate' else 'evaluate.py')
            with target.open('a') as out:out.write('\n# checkpoint falsifier\n')
        result=subprocess.run([sys.executable,'run.py'],cwd=work,env=env,capture_output=True,text=True,timeout=25)
        (work/'rejection.log').write_text(result.stdout+result.stderr)
        expected='RECOVERY_HOLD_NO_ACCEPTED_PROPOSAL' if case=='missing-checkpoint' else 'RECOVERY_HOLD_CHECKPOINT_MISMATCH'
        assert result.returncode!=0 and expected in result.stdout+result.stderr,(case,result.returncode)
        assert len(calls)==before_calls,case
        negative[case]={'exit':result.returncode,'reason':expected,'new_requests':0}
    second=launch('caller-b');second.wait(timeout=120);assert second.returncode==0
    after=archive();assert [x[1] for x in after]==[0,1,2],after
    assert before[0] in after and len(calls)==2,(before_calls,len(calls))
    verification={}
    for generation in (1,2):
        directory=p/f'results/gen_{generation}/results'
        metrics=json.loads((directory/'metrics.json').read_text())
        assert metrics['public']['trial_count']==8 and metrics['public']['reason']=='COMPLETE'
        verification[str(generation)]=independent_verify(directory/'accepted.pck')
    third=launch('terminal-replay');third.wait(timeout=40)
    assert third.returncode==0 and archive()==after and len(calls)==2
    receipt={'status':'PASS','live_provider_calls':0,'fixture_requests':len(calls),'requests_before_kill':before_calls,'requests_for_resumed_generation':0,'archive_before':before,'archive_after':after,'caller_a_returncode':first.returncode,'caller_b_returncode':second.returncode,'terminal_replay_returncode':third.returncode,'independent_geometry':verification,'elapsed_seconds':time.monotonic()-started,'operator_actions_during_run':0,'claim_ceiling':'Temporary patched Shinka copy; cached model responses; caller plus descendants killed after accepted checkpoint; two native evaluated generations and separate exact checker. Not live proposal recovery, distinct security principal, host failure or production deployment.'}
    receipt.update(negative_cases=negative, concurrent_caller_rejected=True)
    (p/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
finally:
    server.shutdown()
    for child,stream in children:
        if child.poll() is None:kill_tree(child)
        stream.close()
