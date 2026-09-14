"""Thin native supervisor adapter: Shinka owns search; DO/Workflow owns the job.

No provider credentials, scheduler, lease database or inference retry loop.
systemd owns bounded process replacement. The fixed evaluator is unchanged.
"""
import hashlib,json,os,signal,sqlite3,subprocess,sys,threading,time,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import psutil
from context import cleave

ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)
URL=os.environ['WORK_CELL_URL']
assert URL.startswith('https://') and URL.endswith('/vps/work-cell')
manifest=json.loads((ROOT/'manifest.json').read_text())
for name,digest in manifest['context']['files'].items():
    assert Path(name).name==name and hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,('SOURCE_DRIFT',name)

def api(action,body=None):
    data=json.dumps({'action':action,'input':body,'work_id':manifest['work_id']},separators=(',',':')).encode()
    # Existing IP-bound Worker admission; no credentials enter candidate files.
    call=subprocess.run(['curl','--fail-with-body','--silent','--show-error','--max-time','110','-H','Content-Type: application/json','--data-binary','@-',URL],input=data,capture_output=True,timeout=115)
    if call.returncode:raise RuntimeError('CELL_HTTP_HOLD '+call.stdout.decode()[:300])
    value=json.loads(call.stdout)
    if value.get('error'):raise RuntimeError('CELL_REFUSED '+str(value['error'])[:200])
    return value

state=api('admit',manifest)
assert state['state']=='RUNNING' and time.time()*1000<state['deadline_ms'],'MISSION_NOT_RUNNING'
reported={g['generation'] for g in state['generations']}
winner=any(g['proof'].get('winner') for g in state['generations'])
episode=uuid.uuid4().hex
event_path=ROOT/'supervisor-receipt.json'
episodes=json.loads(event_path.read_text()).get('episodes',[]) if event_path.exists() else []
assert len(episodes)<2,'RESTART_CAP'
episodes.append({'episode_id':episode,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'restored_generations':sorted(reported)})
def record(**fields):
    episodes[-1].update(fields)
    tmp=event_path.with_suffix('.tmp');tmp.write_text(json.dumps({'work_id':manifest['work_id'],'episodes':episodes},indent=2));os.replace(tmp,event_path)
record(state='RUNNING')
failure=threading.Event()
failure_detail=[]

def generation_ready(g):
    db=ROOT/'results/programs.sqlite'
    if not db.exists():return False
    try:
        with sqlite3.connect(f'file:{db}?mode=ro',uri=True) as con:
            return con.execute('select count(*) from programs where generation=?',(g,)).fetchone()[0]==1
    except sqlite3.OperationalError:return False

report_lock=threading.Lock()
def report_generation(g):
    global winner
    with report_lock:
        if g in reported:return
        if not generation_ready(g):return
        folder=ROOT/f'results/gen_{g}'
        metrics=json.loads((folder/'results/metrics.json').read_text())['public']
        result=api('generation',{'generation':g,'program_sha256':hashlib.sha256((folder/'main.py').read_bytes()).hexdigest(),'content':(folder/'results/accepted.pck').read_text(),'metrics':metrics})
        assert result.get('accepted') is True,'VERIFIER_ACK_MISSING'
        winner=winner or result['receipt']['proof'].get('winner',False)
        reported.add(g);record(verified_generations=sorted(reported))

class Proxy(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        try:
            if self.path.endswith('/stop'):
                result=api('stop')
            else:
                n=int(self.headers.get('Content-Length','0'));assert 0<n<=32000,'INPUT_BOUND'
                request=cleave(json.loads(self.rfile.read(n)),manifest['context']['system_prefix'])
                assert self.path.endswith('/chat/completions'),'ROUTE'
                # Cleave at the verified-result boundary before admitting the next
                # neural turn. This wait performs no model calls or retries.
                current=api('status');rows=current['input_rows'] if manifest.get('proposal_source')=='admitted-input' else current['budget']['rows'];count=len(rows)
                if current['budget']['state']=='STOPPED':raise RuntimeError('PROVIDER_HOLD')
                if count and count not in reported and not any(r.get('input_sha256')==hashlib.sha256(json.dumps(request,separators=(',',':'),ensure_ascii=False).encode()).hexdigest() for r in rows):
                    deadline=time.monotonic()+55
                    while not generation_ready(count) and time.monotonic()<deadline and child.poll() is None:time.sleep(.2)
                    report_generation(count)
                result=api('model',request)
                if result.get('error'):raise RuntimeError('PROVIDER_HOLD')
            raw=json.dumps(result).encode();self.send_response(200)
        except Exception as error:
            failure_detail.append(str(error)[:300])
            failure.set()
            raw=json.dumps({'error':{'message':str(error)[:300]}}).encode();self.send_response(400)
        self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers()
        try:self.wfile.write(raw)
        except (BrokenPipeError,ConnectionResetError):pass

server=ThreadingHTTPServer(('127.0.0.1',0),Proxy)
env=dict(os.environ,SHINKA_EVAL_CHECKPOINT='1',CELL_API_URL=f'http://127.0.0.1:{server.server_port}/v1',XDG_CACHE_HOME=str(ROOT/'cache'))
# Keep stop-on-win within the existing mission policy.
env['CELL_STOP_URL']=f'http://127.0.0.1:{server.server_port}/stop'
log=(ROOT/f'caller-{len(episodes)}.log').open('w')
child=subprocess.Popen([sys.executable,'run.py'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
threading.Thread(target=server.serve_forever,daemon=True).start()

def kill_owned():
    if child.poll() is not None:return
    os.killpg(child.pid,signal.SIGSTOP)
    try:
        for descendant in psutil.Process(child.pid).children(recursive=True):
            try:descendant.kill()
            except psutil.NoSuchProcess:pass
    except psutil.NoSuchProcess:pass
    os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=10)

try:
    while child.poll() is None:
        if failure.is_set():raise RuntimeError('PROVIDER_HOLD')
        if time.time()*1000>=state['deadline_ms']:raise RuntimeError('MISSION_DEADLINE')
        checkpoint=ROOT/'results/gen_1/accepted-proposal.json'
        marker=ROOT/'interruption-injected'
        if os.environ.get('WORK_CELL_INTERRUPT_ONCE')=='1' and not marker.exists() and checkpoint.exists():
            kill_owned();marker.write_text(episode);record(state='INTERRUPTED_FOR_RECOVERY_ASSAY',caller_exit=child.returncode)
            raise SystemExit(75)
        for g in (1,2):report_generation(g)
        if winner:kill_owned();break
        time.sleep(.1)
    assert child.returncode==0 or winner,('CALLER_FAILED',child.returncode)
    if not winner:
        for g in (1,2):
            report_generation(g)
            if winner:break
    assert reported=={1,2} or winner,'MISSING_VERIFIED_GENERATION'
    final=api('finish')
    limit=time.monotonic()+40
    while final.get('native',{}).get('status') not in ('complete','completed') and time.monotonic()<limit:
        time.sleep(2);final=api('status')
    assert final.get('native',{}).get('status') in ('complete','completed'),'NATIVE_WORKFLOW_NOT_COMPLETE'
    native_result=final['native'].get('output',{})
    assert native_result.get('status')=='completed' and native_result.get('result',{}).get('verdict')=='accept','NATIVE_RESULT_REJECTED'
    assert native_result['result'].get('output_sha256')==final['result']['output_sha256'],'NATIVE_RESULT_BINDING'
    (ROOT/'final.json').write_text(json.dumps(final,indent=2));record(state='COMPLETED',verified_generations=sorted(reported),native_status=final['native']['status'])
    print(json.dumps({'state':'COMPLETED','verified_generations':len(reported),'winner':winner,'supervisor_episodes':len(episodes),'work_id':manifest['work_id']}))
except Exception as error:
    kill_owned()
    reason='PROVIDER_HOLD' if failure.is_set() else 'DEADLINE' if time.time()*1000>=state['deadline_ms'] else 'CALLER_FAILED'
    record(state='FAILED',reason=reason,error=str(error)[:300],handoff_errors=failure_detail[:2])
    try:
        final=api('fail',{'reason':reason})
        limit=time.monotonic()+40
        while final.get('native',{}).get('status') not in ('complete','completed') and time.monotonic()<limit:
            time.sleep(2);final=api('status')
        (ROOT/'failure.json').write_text(json.dumps(final,indent=2))
        record(native_status=final.get('native',{}).get('status'))
    except Exception as close_error:record(closeout_error=str(close_error)[:300])
    # Native RestartPreventExitStatus=78 makes a known failed job terminal.
    raise SystemExit(78)
finally:
    kill_owned();server.shutdown();log.close()
