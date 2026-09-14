import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
import workcell_runtime_v1 as rt


def write_task(root, name, wid, priority=0, admitted=True, blocked=False, schema="hfo.research-workitem.v1"):
    task = {
        "schema": schema,
        "work_id": wid,
        "priority": priority,
        "admitted": admitted,
        "blocked": blocked,
        "question": "held-out",
        "cloudflare_health_url": "https://example.invalid/health",
        "sources": [],
    }
    path = root / name
    path.write_text(json.dumps(task, indent=2), encoding="utf-8")
    return path


def fake_worker_script(root, exit_code=0):
    path = root / "fake_worker.py"
    path.write_text(
        "import hashlib,json,sys\n"
        "from pathlib import Path\n"
        f"raise SystemExit({exit_code})\n" if exit_code else
        "import hashlib,json,sys\nfrom pathlib import Path\n"
        "task=json.loads(Path(sys.argv[1]).read_text())\n"
        "out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)\n"
        "base={'schema':'hfo.research-cell-result.v1','work_id':task['work_id'],'verdict':'PASS','sources':[],'next_state':'RETIRE','tao_hot_loop_actions':0}\n"
        "base['result_sha256']=hashlib.sha256(json.dumps(base,sort_keys=True,separators=(',',':')).encode()).hexdigest()\n"
        "(out/'result.json').write_text(json.dumps(base))\n"
        "(out/'report.md').write_text('held-out report')\n",
        encoding="utf-8",
    )
    return path


class FakeGitHub:
    def __init__(self, initial_bodies=None, fail_comment=False, fail_dispatch=False):
        self.comments = [{"body": b, "html_url": f"https://example/{i}"} for i, b in enumerate(initial_bodies or [])]
        self.fail_comment = fail_comment
        self.fail_dispatch = fail_dispatch
        self.calls = []

    def api(self, token, method, path, payload=None):
        self.calls.append((method, path, payload))
        if method == "GET" and "/comments?" in path:
            return 200, list(self.comments)
        if method == "POST" and path.endswith("/comments"):
            if self.fail_comment:
                raise RuntimeError("HELDOUT_COMMENT_FAILURE")
            row = {"body": payload["body"], "html_url": f"https://example/ack-{len(self.comments)+1}", "id": len(self.comments)+1}
            self.comments.append(row)
            return 201, row
        if method == "POST" and "/actions/workflows/" in path:
            if self.fail_dispatch:
                raise RuntimeError("HELDOUT_DISPATCH_FAILURE")
            return 204, None
        raise AssertionError((method, path, payload))

    @property
    def effect_calls(self):
        return [c for c in self.calls if c[0] == "POST"]


class WorkCellHeldOutBehavior(unittest.TestCase):
    def run_main(self, tasks, gh, worker, outdir):
        argv = ["workcell_runtime_v1.py", "--task-dir", str(tasks), "--issue", "13", "--workflow", "workcell-runtime-v1.yml", "--outdir", str(outdir), "--repo", "owner/repo"]
        env = {"GH_TOKEN": "heldout", "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1"}
        with patch.object(sys, "argv", argv), patch.dict(os.environ, env, clear=False), patch.object(rt, "api", gh.api), patch.object(rt, "worker_for", return_value=worker):
            with contextlib.redirect_stdout(io.StringIO()):
                return rt.main()

    def test_blocked_high_priority_is_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            write_task(tasks,'blocked.json','BLOCKED',999,blocked=True)
            write_task(tasks,'allowed.json','ALLOWED',1)
            gh=FakeGitHub(); worker=fake_worker_script(root)
            self.assertEqual(self.run_main(tasks,gh,worker,out),0)
            receipt=json.loads((out/'runtime-receipt.json').read_text())
            self.assertEqual(receipt['work_id'],'ALLOWED')
            self.assertEqual(receipt['tao_hot_loop_actions'],0)

    def test_retired_work_is_noop_without_effects(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            p=write_task(tasks,'a.json','A',1)
            marker=f"<!-- hfo-research-cell-r0:A:{rt.hashlib.sha256(p.read_bytes()).hexdigest()} -->"
            gh=FakeGitHub([marker]); worker=fake_worker_script(root)
            self.assertEqual(self.run_main(tasks,gh,worker,out),0)
            receipt=json.loads((out/'runtime-receipt.json').read_text())
            self.assertEqual(receipt['status'],'NOOP')
            self.assertEqual(gh.effect_calls,[])

    def test_worker_failure_has_no_github_effects(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            write_task(tasks,'a.json','A',1)
            gh=FakeGitHub(); worker=fake_worker_script(root,7)
            with self.assertRaises(Exception):
                self.run_main(tasks,gh,worker,out)
            self.assertEqual(gh.effect_calls,[])

    def test_consumer_ack_failure_stops_before_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            write_task(tasks,'a.json','A',2); write_task(tasks,'b.json','B',1)
            gh=FakeGitHub(fail_comment=True); worker=fake_worker_script(root)
            with self.assertRaises(RuntimeError):
                self.run_main(tasks,gh,worker,out)
            self.assertFalse(any('/actions/workflows/' in p for m,p,_ in gh.effect_calls))

    def test_dispatch_failure_must_not_durably_retire_current_work(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            a=write_task(tasks,'a.json','A',2); write_task(tasks,'b.json','B',1)
            gh=FakeGitHub(fail_dispatch=True); worker=fake_worker_script(root)
            with self.assertRaises(RuntimeError):
                self.run_main(tasks,gh,worker,out)
            marker=f"<!-- hfo-research-cell-r0:A:{rt.hashlib.sha256(a.read_bytes()).hexdigest()} -->"
            self.assertFalse(any(marker in row['body'] for row in gh.comments), 'failed continuation must not look retired')

    def test_duplicate_ids_fail_before_effects(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            write_task(tasks,'a.json','DUP',2); write_task(tasks,'b.json','DUP',1)
            gh=FakeGitHub(); worker=fake_worker_script(root)
            with self.assertRaises(SystemExit):
                self.run_main(tasks,gh,worker,out)
            self.assertEqual(gh.effect_calls,[])


if __name__ == '__main__':
    unittest.main()
