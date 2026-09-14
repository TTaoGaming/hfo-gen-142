import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tools import janitor_gate as jg

ROOT = Path(__file__).resolve().parents[1]
EXEC = ROOT / "ops" / "janitor_exec.py"


class JanitorGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.now = datetime.now(timezone.utc).replace(microsecond=0)

    def tearDown(self):
        self.temp.cleanup()

    def make_dir(self, name="owned", kind="TEMP_DIR"):
        target = self.root / name
        target.mkdir(parents=True)
        (target / "payload.txt").write_text("scratch", encoding="utf-8")
        resource_id = f"res:{name}"
        work_ref = f"work:{name}"
        (target / ".hfo-cleanup-owner.json").write_text(json.dumps({
            "schema": jg.OWNER_SCHEMA,
            "resource_id": resource_id,
            "owner_work_ref": work_ref,
        }), encoding="utf-8")
        return target, self.doc(target, resource_id, work_ref, kind)

    def doc(self, target, resource_id="res:x", work_ref="work:x", kind="TEMP_DIR"):
        return {
            "schema": jg.SCHEMA,
            "cleanup_id": "cleanup:test",
            "actor_owner": jg.SEMANTIC_OWNER,
            "work_ref": work_ref,
            "requested_action": jg.ACTION_BY_KIND[kind],
            "resource": {
                "resource_id": resource_id,
                "kind": kind,
                "target": str(target),
                "owner_work_ref": work_ref,
                "expires_utc": (self.now - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
                "disposable": True,
                "protected": False,
                "external_effect": False,
            },
            "observed": {
                "observed_utc": (self.now - timedelta(seconds=10)).isoformat().replace("+00:00", "Z"),
                "exists": True,
                "identity_match": True,
                "active_lease": False,
                "pending_consumers": 0,
                "terminal_state": "PASS",
                "durable_evidence_ref": "github:TTaoGaming/hfo-gen-142#13:fixture",
                "evidence_sha256": "a" * 64,
                "self_attested": False,
            },
        }

    def admit(self, doc):
        return jg.evaluate(doc, [str(self.root)], now=self.now)

    def test_expired_owned_temp_dir_is_admitted(self):
        _, doc = self.make_dir()
        self.assertEqual(self.admit(doc)["decision"], "ADMIT_CLEANUP")

    def test_live_ttl_is_refused(self):
        _, doc = self.make_dir()
        doc["resource"]["expires_utc"] = (self.now + timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
        self.assertEqual(self.admit(doc)["code"], "CLEANUP_TTL_LIVE")

    def test_active_lease_is_refused(self):
        _, doc = self.make_dir()
        doc["observed"]["active_lease"] = True
        self.assertEqual(self.admit(doc)["code"], "CLEANUP_ACTIVE_LEASE")

    def test_pending_consumer_is_refused(self):
        _, doc = self.make_dir()
        doc["observed"]["pending_consumers"] = 1
        self.assertEqual(self.admit(doc)["code"], "CLEANUP_PENDING_CONSUMER")

    def test_self_attested_evidence_is_refused(self):
        _, doc = self.make_dir()
        doc["observed"]["self_attested"] = True
        self.assertEqual(self.admit(doc)["code"], "CLEANUP_SELF_ATTESTED_EVIDENCE")

    def test_bad_evidence_hash_is_refused(self):
        _, doc = self.make_dir()
        doc["observed"]["evidence_sha256"] = "not-a-hash"
        self.assertEqual(self.admit(doc)["code"], "CLEANUP_EVIDENCE_SHA_INVALID")

    def test_outside_allow_root_is_refused(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / "x"
            target.mkdir()
            doc = self.doc(target)
            self.assertEqual(self.admit(doc)["code"], "CLEANUP_TARGET_OUTSIDE_ALLOW_ROOT")

    def test_allow_root_itself_is_refused(self):
        doc = self.doc(self.root)
        self.assertEqual(self.admit(doc)["code"], "CLEANUP_TARGET_OUTSIDE_ALLOW_ROOT")

    def test_marker_mismatch_is_refused(self):
        target, doc = self.make_dir()
        marker = json.loads((target / ".hfo-cleanup-owner.json").read_text())
        marker["owner_work_ref"] = "work:other"
        (target / ".hfo-cleanup-owner.json").write_text(json.dumps(marker), encoding="utf-8")
        self.assertEqual(self.admit(doc)["code"], "OWNER_MARKER_MISMATCH")

    def test_absent_resource_is_idempotent_noop(self):
        target = self.root / "gone"
        doc = self.doc(target, "res:gone", "work:gone")
        doc["observed"]["exists"] = False
        self.assertEqual(self.admit(doc)["decision"], "NOOP_CLEAN")

    def make_worktree(self):
        repo = self.root / "repo"
        wt = self.root / "worktrees" / "w1"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
        (repo / "base.txt").write_text("base", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "base.txt"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
        wt.parent.mkdir()
        subprocess.run(["git", "-C", str(repo), "worktree", "add", "-qb", "cleanup-test", str(wt)], check=True)
        doc = self.doc(wt, "res:wt", "work:wt", "WORKTREE")
        doc["resource"]["repo_root"] = str(repo)
        return repo, wt, doc

    def test_clean_registered_worktree_is_admitted(self):
        _, _, doc = self.make_worktree()
        self.assertEqual(self.admit(doc)["decision"], "ADMIT_CLEANUP")

    def test_dirty_worktree_is_refused(self):
        _, wt, doc = self.make_worktree()
        (wt / "dirty.txt").write_text("dirty", encoding="utf-8")
        self.assertEqual(self.admit(doc)["code"], "WORKTREE_DIRTY")

    def test_leaf_executor_deletes_only_admitted_temp_dir(self):
        target, doc = self.make_dir("exec")
        request = self.root / "request.json"
        receipt = self.root / "receipt.json"
        request.write_text(json.dumps(doc), encoding="utf-8")
        proc = subprocess.run([
            sys.executable, str(EXEC), "--request", str(request), "--receipt", str(receipt),
            "--allowed-root", str(self.root),
        ], text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse(target.exists())
        self.assertEqual(json.loads(receipt.read_text())["status"], "CLEANED")

    def test_leaf_executor_does_not_delete_refused_target(self):
        target, doc = self.make_dir("held")
        doc["observed"]["active_lease"] = True
        request = self.root / "request-held.json"
        receipt = self.root / "receipt-held.json"
        request.write_text(json.dumps(doc), encoding="utf-8")
        proc = subprocess.run([
            sys.executable, str(EXEC), "--request", str(request), "--receipt", str(receipt),
            "--allowed-root", str(self.root),
        ], text=True, capture_output=True, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertTrue(target.exists())
        self.assertEqual(json.loads(receipt.read_text())["status"], "HOLD_GATE")

    def test_leaf_executor_removes_clean_worktree_without_deleting_branch(self):
        repo, wt, doc = self.make_worktree()
        request = self.root / "request-wt.json"
        receipt = self.root / "receipt-wt.json"
        request.write_text(json.dumps(doc), encoding="utf-8")
        proc = subprocess.run([
            sys.executable, str(EXEC), "--request", str(request), "--receipt", str(receipt),
            "--allowed-root", str(self.root),
        ], text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse(wt.exists())
        branches = subprocess.run(["git", "-C", str(repo), "branch", "--list", "cleanup-test"], text=True, capture_output=True, check=True).stdout
        self.assertIn("cleanup-test", branches)


if __name__ == "__main__":
    unittest.main()
