"""Zero-provider regression against the installed Shinka scheduler."""
import hashlib,json,sys,time
from pathlib import Path
from types import SimpleNamespace
from shinka.launch.scheduler import JobScheduler,LocalJobConfig
from shinka.launch.local import submit
import shinka.launch.scheduler as scheduler_module

p=Path(sys.argv[1]);p.mkdir(exist_ok=False)
results={}
scheduler=JobScheduler('local',LocalJobConfig(time='00:00:50'),verbose=True,max_workers=1)
for label,proposal_age,evaluation_age in [('slow_proposal_fresh_evaluation',90,0),('expired_evaluation',90,60)]:
    process=submit(str(p/label),[sys.executable,'-c','import time;time.sleep(2)'])
    job=SimpleNamespace(job_id=process,start_time=time.time()-proposal_age,evaluation_started_at=time.time()-evaluation_age,evaluation_submitted_at=time.time()-evaluation_age,generation=1)
    running=scheduler.check_job_status(job)
    if process.poll() is None:process.terminate()
    process.wait();process.cleanup_logging()
    results[label]={'running':running,'returncode':process.returncode}
results['scheduler_sha256']=hashlib.sha256(Path(scheduler_module.__file__).read_bytes()).hexdigest()
results['provider_calls']=0
(p/'receipt.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
scheduler.executor.shutdown()
