import contextlib
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import terminal_handoff_gate as gate
import workcell_runtime_v1 as runtime


class WorkCellRuntimeTest(unittest.TestCase):
    def gate(self, doc):
        with contextlib.redirect_stdout(io.StringIO()):
            return gate.evaluate(doc)

    def test_mission_complete_handoff_passes(self):
        result = {"work_id": "W1", "result_sha256": "a" * 64, "sources": []}
        handoff = runtime.build_handoff(result, "https://github.com/x/y/issues/1#issuecomment-1", None)
        self.assertEqual(self.gate(handoff), 0)
        self.assertEqual(handoff["next"]["mode"], "MISSION_COMPLETE")

    def test_auto_dispatch_handoff_passes(self):
        receipt = {
            "receipt_type": "github_workflow_dispatch", "owner": "github-actions",
            "receipt_id": "1:1:W2", "status": "ACCEPTED",
            "observed_utc": "2026-09-14T22:00:00Z",
            "provenance_ref": "https://api.github.com/repos/x/y/actions/workflows/workcell-runtime-v1.yml/dispatches",
            "receipt_sha256": "b" * 64, "self_attested": False,
            "work_ref": "github:x/y:WORKCELLS/research-r0/w2.json",
        }
        result = {"work_id": "W1", "result_sha256": "a" * 64, "sources": [{}]}
        handoff = runtime.build_handoff(result, "https://github.com/x/y/issues/1#issuecomment-1", receipt)
        self.assertEqual(self.gate(handoff), 0)
        self.assertEqual(handoff["next"]["mode"], "AUTO_DISPATCH")

    def test_unknown_worker_schema_fails_closed(self):
        with self.assertRaises(RuntimeError):
            runtime.worker_for({"schema": "hfo.unknown.v9"})


if __name__ == "__main__":
    unittest.main()
