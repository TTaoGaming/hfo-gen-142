"""POSIX supervisor falsifiers. All remote operations and science are fixtures."""
import hashlib,json,os,runpy,subprocess,sys,tempfile,time
from pathlib import Path
from unittest.mock import patch

source=Path(__file__).resolve().parent
original_run=subprocess.run
results=[]
for case in ('provider-hold','rejected-native-result'):
    root=Path(tempfile.mkdtemp(prefix='supervisor-fixture-',dir=Path.cwd()))
    for name in ('supervisor.py','context.py'):(root/name).write_bytes((source/name).read_bytes())
    manifest={'work_id':'fixture-'+case,'context':{'files':{},'system_prefix':'Fixed policy'}}
    (root/'manifest.json').write_text(json.dumps(manifest))
    child_source="""import os,json,time,urllib.request
from pathlib import Path
Path('child.pid').write_text(str(os.getpid()))
try:
 request=urllib.request.Request(os.environ['CELL_API_URL']+'/chat/completions',data=json.dumps({'model':'packing-cell','messages':[{'role':'system','content':'Fixed policy\\nFormat A'},{'role':'user','content':'delta'}]}).encode(),headers={'Content-Type':'application/json'})
 urllib.request.urlopen(request,timeout=5).read()
except Exception:pass
time.sleep(20)
"""
    if case=='rejected-native-result':
        child_source="""import sqlite3,json,os
from pathlib import Path
Path('child.pid').write_text(str(os.getpid()))
Path('results').mkdir()
with sqlite3.connect('results/programs.sqlite') as db:
 db.execute('create table programs (generation integer)')
 for g in (1,2):
  p=Path(f'results/gen_{g}');(p/'results').mkdir(parents=True)
  (p/'main.py').write_text(str(g));(p/'results/accepted.pck').write_text('fixture')
  (p/'results/metrics.json').write_text(json.dumps({'public':{'reason':'COMPLETE','trial_count':8}}))
  db.execute('insert into programs values (?)',(g,))
"""
    (root/'run.py').write_text(child_source)
    actions=[]
    def fixture(args,**kwargs):
        if args[0]!='curl':return original_run(args,**kwargs)
        body=json.loads(kwargs['input']);action=body['action'];actions.append(action)
        if action in ('admit','status'):
            value={'state':'RUNNING','deadline_ms':time.time()*1000+20000,'generations':[],'input_rows':[],'budget':{'state':'RUNNING','rows':[]}}
        elif action=='model':value={'error':{'message':'AMBIGUOUS_NO_RETRY'}}
        elif action=='generation':value={'accepted':True,'receipt':{'proof':{'winner':False}}}
        elif action=='finish':value={'native':{'status':'complete','output':{'status':'rejected','result':{'verdict':'reject'}}},'result':{'output_sha256':'a'*64}}
        elif action=='fail':value={'native':{'status':'complete','output':{'status':'rejected'}}}
        else:raise AssertionError(action)
        return subprocess.CompletedProcess(args,0,json.dumps(value).encode(),b'')
    before=time.monotonic();previous=Path.cwd();sys.path.insert(0,str(root))
    with patch.dict(os.environ,{'WORK_CELL_URL':'https://fixture.invalid/vps/work-cell'}),patch.object(subprocess,'run',fixture):
        try:runpy.run_path(str(root/'supervisor.py'),run_name='__main__')
        except SystemExit as e:exit_code=e.code
        else:exit_code=0
    os.chdir(previous);sys.path.pop(0)
    elapsed=time.monotonic()-before
    assert exit_code==78,(case,exit_code)
    assert actions.count('fail')==1 and actions.count('model')==int(case=='provider-hold'),actions
    pid=int((root/'child.pid').read_text())
    try:os.kill(pid,0)
    except ProcessLookupError:pass
    else:raise AssertionError('ORPHANED_CHILD')
    receipt=json.loads((root/'supervisor-receipt.json').read_text())
    if case=='rejected-native-result':assert receipt['episodes'][0]['error']=='NATIVE_RESULT_REJECTED'
    assert elapsed<10,(case,elapsed)
    results.append({'case':case,'exit':exit_code,'child_gone':True,'closeout_count':actions.count('fail'),'elapsed_seconds':elapsed})
print(json.dumps({'status':'PASS','cases':results,'live_provider_calls':0,'supervisor_sha256':hashlib.sha256((source/'supervisor.py').read_bytes()).hexdigest()}))
