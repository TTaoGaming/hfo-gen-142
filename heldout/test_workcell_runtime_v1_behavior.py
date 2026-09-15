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


def current_marker(path, wid):
    return f"<!-- hfo-workcell-v1:{wid}:{rt.hashlib.sha256(path.read_bytes()).hexdigest()} -->"


def ack_marker(path, wid):
    return f"<!-- hfo-workcell-ack-v1:{wid}:{rt.hashlib.sha256(path.read_bytes()).hexdigest()} -->"


def fake_worker_script(root, exit_code=0):
    path = root / "fake_worker.py"
    if exit_code:
        body = f"raise SystemExit({exit_code})\n"
    else:
        body = (
            "import hashlib,json,sys\nfrom pathlib import Path\n"
            "task_path=Path(sys.argv[1]); task=json.loads(task_path.read_text())\n"
            "out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)\n"
            "spec_sha=hashlib.sha256(task_path.read_bytes()).hexdigest()\n"
            "base={'schema':'hfo.research-cell-result.v1','work_id':task['work_id'],'spec_sha256':spec_sha,'verdict':'PASS','sources':[],'next_state':'RETIRE','tao_hot_loop_actions':0}\n"
            "base['result_sha256']=hashlib.sha256(json.dumps(base,sort_keys=True,separators=(',',':')).encode()).hexdigest()\n"
            "(out/'result.json').write_text(json.dumps(base))\n"
            "(out/'report.md').write_text('held-out report')\n"
        )
    path.write_text(body, encoding="utf-8")
    return path


class FakeGitHub:
    def __init__(self, initial_bodies=None, fail_ack=False, fail_watch=False, fail_retirement=False):
        self.comments = [{"body": b, "html_url": f"https://example/{i}"} for i, b in enumerate(initial_bodies or [])]
        self.fail_ack = fail_ack
        self.fail_watch = fail_watch
        self.fail_retirement = fail_retirement
        self.calls = []

    def api(self, token, method, path, payload=None):
        self.calls.append((method, path, payload))
        if method == "GET" and "/comments?" in path:
            return 200, list(self.comments)
        if method == "GET" and "/actions/workflows/" in path:
            if self.fail_watch:
                raise RuntimeError("HELDOUT_WATCH_FAILURE")
            return 200, {"id": 77, "state": "active", "path": ".github/workflows/workcell-runtime-v1.yml"}
        if method == "POST" and path.endswith("/comments"):
            body = payload["body"]
            if self.fail_ack and "hfo-workcell-ack-v1" in body:
                raise RuntimeError("HELDOUT_ACK_FAILURE")
            if self.fail_retirement and "hfo-workcell-v1:" in body:
                raise RuntimeError("HELDOUT_RETIREMENT_FAILURE")
            row = {"body": body, "html_url": f"https://example/comment-{len(self.comments)+1}", "id": len(self.comments)+1}
            self.comments.append(row)
            return 201, row
        if method == "POST" and "/actions/workflows/" in path:
            raise AssertionError("recursive dispatch is forbidden in held-out v1 behavior")
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
            gh=FakeGitHub([current_marker(p,'A')]); worker=fake_worker_script(root)
            self.assertEqual(self.run_main(tasks,gh,worker,out),0)
            receipt=json.loads((out/'runtime-receipt.json').read_text())
            self.assertEqual(receipt['status'],'NOOP')
            self.assertEqual(gh.effect_calls,[])

    def test_worker_failure_writes_only_typed_failure_not_success_or_retirement(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            a=write_task(tasks,'a.json','A',1)
            gh=FakeGitHub(); worker=fake_worker_script(root,7)
            self.assertEqual(self.run_main(tasks,gh,worker,out),0)
            receipt=json.loads((out/'runtime-receipt.json').read_text())
            self.assertEqual(receipt['status'],'RETRY_ARMED')
            self.assertEqual(len(gh.effect_calls),1)
            body=gh.effect_calls[0][2]['body']
            self.assertIn('hfo-workcell-failure-v1:A:',body)
            self.assertNotIn('hfo-workcell-ack-v1:A:',body)
            self.assertNotIn(current_marker(a,'A'),body)

    def test_poison_pill_quarantines_then_next_work_progresses(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir()
            a=write_task(tasks,'a.json','A',99); b=write_task(tasks,'b.json','B',1)
            task=json.loads(a.read_text()); task['max_attempts']=2; a.write_text(json.dumps(task),encoding='utf-8')
            gh=FakeGitHub(); bad=fake_worker_script(root,7)
            out1=root/'out1'; out2=root/'out2'; out3=root/'out3'
            self.assertEqual(self.run_main(tasks,gh,bad,out1),0)
            self.assertEqual(json.loads((out1/'runtime-receipt.json').read_text())['status'],'RETRY_ARMED')
            self.assertEqual(self.run_main(tasks,gh,bad,out2),0)
            r2=json.loads((out2/'runtime-receipt.json').read_text())
            self.assertEqual(r2['status'],'QUARANTINED')
            self.assertEqual(r2['next_work_id'],'B')
            qmarker=f"<!-- hfo-workcell-quarantine-v1:A:{rt.hashlib.sha256(a.read_bytes()).hexdigest()} -->"
            self.assertTrue(any(qmarker in row['body'] for row in gh.comments))
            good=fake_worker_script(root,0)
            self.assertEqual(self.run_main(tasks,gh,good,out3),0)
            r3=json.loads((out3/'runtime-receipt.json').read_text())
            self.assertEqual(r3['work_id'],'B')

    def test_consumer_ack_failure_stops_before_retirement(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            a=write_task(tasks,'a.json','A',1)
            gh=FakeGitHub(fail_ack=True); worker=fake_worker_script(root)
            with self.assertRaises(RuntimeError):
                self.run_main(tasks,gh,worker,out)
            self.assertFalse(any(current_marker(a,'A') in row['body'] for row in gh.comments))

    def test_watch_failure_must_not_durably_retire_current_work(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            a=write_task(tasks,'a.json','A',2); write_task(tasks,'b.json','B',1)
            gh=FakeGitHub(fail_watch=True); worker=fake_worker_script(root)
            with self.assertRaises(RuntimeError):
                self.run_main(tasks,gh,worker,out)
            self.assertTrue(any(ack_marker(a,'A') in row['body'] for row in gh.comments))
            self.assertFalse(any(current_marker(a,'A') in row['body'] for row in gh.comments))

    def test_terminal_gate_failure_must_not_retire(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            a=write_task(tasks,'a.json','A',1)
            gh=FakeGitHub(); worker=fake_worker_script(root)
            with patch.object(rt, 'run_terminal_gate', side_effect=RuntimeError('HELDOUT_GATE_FAILURE')):
                with self.assertRaises(RuntimeError):
                    self.run_main(tasks,gh,worker,out)
            self.assertTrue(any(ack_marker(a,'A') in row['body'] for row in gh.comments))
            self.assertFalse(any(current_marker(a,'A') in row['body'] for row in gh.comments))

    def test_retirement_write_failure_reuses_consumer_ack_on_retry(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out1=root/'out1'; out2=root/'out2'
            a=write_task(tasks,'a.json','A',1)
            gh=FakeGitHub(fail_retirement=True); worker=fake_worker_script(root)
            with self.assertRaises(RuntimeError):
                self.run_main(tasks,gh,worker,out1)
            ack_count=lambda: sum(ack_marker(a,'A') in row['body'] for row in gh.comments)
            self.assertEqual(ack_count(),1)
            gh.fail_retirement=False
            self.assertEqual(self.run_main(tasks,gh,worker,out2),0)
            self.assertEqual(ack_count(),1)
            self.assertTrue(any(current_marker(a,'A') in row['body'] for row in gh.comments))

    def test_two_wakes_progress_a_to_b_without_recursive_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out1=root/'out1'; out2=root/'out2'; out3=root/'out3'
            write_task(tasks,'a.json','A',2); write_task(tasks,'b.json','B',1)
            gh=FakeGitHub(); worker=fake_worker_script(root)
            self.assertEqual(self.run_main(tasks,gh,worker,out1),0)
            r1=json.loads((out1/'runtime-receipt.json').read_text())
            h1=json.loads((out1/'handoff.json').read_text())
            self.assertEqual(r1['work_id'],'A')
            self.assertEqual(r1['next_work_id'],'B')
            self.assertEqual(r1['continuation_mode'],'SCHEDULED_RECONCILE')
            self.assertEqual(h1['next']['mode'],'RECONCILE')
            self.assertFalse(any('/actions/workflows/' in path for method,path,_ in gh.effect_calls))
            self.assertEqual(self.run_main(tasks,gh,worker,out2),0)
            r2=json.loads((out2/'runtime-receipt.json').read_text())
            self.assertEqual(r2['work_id'],'B')
            self.assertIsNone(r2['next_work_id'])
            self.assertEqual(r2['continuation_mode'],'MISSION_COMPLETE')
            self.assertEqual(self.run_main(tasks,gh,worker,out3),0)
            r3=json.loads((out3/'runtime-receipt.json').read_text())
            self.assertEqual(r3['status'],'NOOP')

    def test_duplicate_ids_fail_before_effects(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); tasks=root/'tasks'; tasks.mkdir(); out=root/'out'
            write_task(tasks,'a.json','DUP',2); write_task(tasks,'b.json','DUP',1)
            gh=FakeGitHub(); worker=fake_worker_script(root)
            with self.assertRaises(ValueError):
                self.run_main(tasks,gh,worker,out)
            self.assertEqual(gh.effect_calls,[])


if __name__ == '__main__':
    unittest.main()
