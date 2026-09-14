"""Fault-injection fixture for stock Shinka; serves cached text, never a provider.

Run under a native supervisor with PrivateNetwork=yes. The HTTP fixture is test
equipment, not a new cell service. Actual model-effect recovery is a separate assay.
"""
import hashlib,json,os,signal,sqlite3,subprocess,sys,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

p=Path(sys.argv[1]).resolve();os.chdir(p)
cached=json.loads((p/'cached-response.json').read_text())
entered=threading.Event();release=threading.Event();requests=[];closed=False
class Fixture(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        global closed
        if self.path.endswith('/stop'):
            closed=True;payload={'stopped':True};status=200
        elif closed:
            payload={'error':{'message':'STOPPED'}};status=400
        else:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<40000:self.send_error(400);return
            body=self.rfile.read(n);requests.append(hashlib.sha256(body).hexdigest())
            if len(requests)==1:entered.set();release.wait(75)
            payload=cached;status=200
        data=json.dumps(payload).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers()
        try:self.wfile.write(data)
        except (BrokenPipeError,ConnectionResetError):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Fixture);threading.Thread(target=server.serve_forever,daemon=True).start()
env=dict(os.environ,CELL_API_URL=f'http://127.0.0.1:{server.server_port}/v1',CELL_STOP_URL=f'http://127.0.0.1:{server.server_port}/stop')
def launch(label):
    stream=(p/f'{label}.log').open('w')
    proc=subprocess.Popen([sys.executable,'run.py'],env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    return proc,stream
def archive():
    with sqlite3.connect('file:results/programs.sqlite?mode=ro',uri=True) as db:
        return db.execute('select id,generation from programs order by generation,id').fetchall()
first,log=launch('caller-a')
try:
    assert entered.wait(60),'NO_FIRST_PROPOSAL'
    before=archive();(p/'before.json').write_text(json.dumps(before));assert before and {r[1] for r in before}=={0}
    os.killpg(first.pid,signal.SIGKILL);first.wait(timeout=10);log.close()
    second,log=launch('caller-b')
    try:second.wait(timeout=100)
    except subprocess.TimeoutExpired:os.killpg(second.pid,signal.SIGKILL);second.wait();raise
    log.close();assert second.returncode==0,'RECOVERY_FAILED'
    after=archive();(p/'after.json').write_text(json.dumps(after));assert {r[1] for r in after}=={0,1};assert all(r in after for r in before)
    assert [r for r in after if r[1]==0]==before,'INITIAL_ARCHIVE_DUPLICATED'
    metrics=json.loads((p/'results/gen_1/results/metrics.json').read_text());assert metrics['public']['trial_count']==8
    calls_before=len(requests)
    third,log=launch('completed-replay')
    try:third.wait(timeout=45)
    except subprocess.TimeoutExpired:os.killpg(third.pid,signal.SIGKILL);third.wait();raise
    log.close();assert third.returncode==0
    assert archive()==after and len(requests)==calls_before,'COMPLETED_REPLAY_DISPATCHED'
    receipt={'status':'PASS','provider_calls':0,'fixture_http_requests':len(requests),'unique_fixture_request_hashes':len(set(requests)),'caller_a_returncode':first.returncode,'caller_b_returncode':second.returncode,'completed_replay_returncode':third.returncode,'archive_before':before,'archive_after':after,'generation_1_metrics':metrics,'claim_ceiling':'Caller process killed during cached proposal; native SQLite resume and terminal replay. No hosted provider-effect or whole-VPS failure claim.'}
    (p/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
finally:
    release.set();server.shutdown()
    if first.poll() is None:os.killpg(first.pid,signal.SIGKILL);first.wait()
