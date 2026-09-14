import copy
import unittest

from tools import reconcile_kernel as rk
from tools import reconcile_snapshot_guard as sg


class ReconcileSnapshotGuardTests(unittest.TestCase):
    def base(self):
        snapshot = {
            "schema": rk.SCHEMA,
            "policy_version": rk.POLICY_VERSION,
            "controller_observed_at": "2026-09-14T21:55:00Z",
            "actor": {
                "owner": rk.ACTOR_OWNER,
                "phase": "IDLE",
                "workitem_id": None,
                "worker_job_available": False,
                "terminal_consumed": True,
                "terminal_ref": None,
            },
            "demand": [],
            "dispatches": [],
            "worker_routes": [],
            "human_boundary": {"active": False},
        }
        kinds = {
            "actor": "cloudflare_api",
            "demand": "github_api",
            "dispatches": "github_actions_api",
            "worker_routes": "vps_controller_api",
            "human_boundary": "static_policy",
        }
        snapshot["observations"] = {
            field: {
                "source_kind": kinds[field],
                "source_ref": f"source:{field}:r0",
                "source_sha256": "1" * 64,
                "value_sha256": rk.digest(snapshot[field]),
                "observed_at": "2026-09-14T21:54:30Z",
                "max_age_s": 60,
                "self_attested": False,
            }
            for field in sg.CONTROL_FIELDS
        }
        return snapshot

    def test_complete_envelope_passes(self):
        result = sg.validate(self.base())
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["checked_fields"], list(sg.CONTROL_FIELDS))

    def test_missing_observation_fails_closed(self):
        snapshot = self.base()
        del snapshot["observations"]["dispatches"]
        result = sg.validate(snapshot)
        self.assertEqual((result["decision"], result["reason"], result["field"]), ("HOLD", "OBSERVATION_MISSING", "dispatches"))

    def test_self_attested_input_is_rejected(self):
        snapshot = self.base()
        snapshot["observations"]["actor"]["self_attested"] = True
        result = sg.validate(snapshot)
        self.assertEqual(result["reason"], "SELF_ATTESTED_OBSERVATION")

    def test_stale_input_is_rejected(self):
        snapshot = self.base()
        snapshot["observations"]["demand"].update({"observed_at": "2026-09-14T21:50:00Z", "max_age_s": 60})
        result = sg.validate(snapshot)
        self.assertEqual((result["decision"], result["reason"], result["field"]), ("HOLD", "OBSERVATION_STALE", "demand"))

    def test_value_mutated_after_observation_is_rejected(self):
        snapshot = self.base()
        snapshot["actor"]["phase"] = "TERMINAL"
        result = sg.validate(snapshot)
        self.assertEqual((result["decision"], result["reason"], result["field"]), ("HOLD", "VALUE_HASH_MISMATCH", "actor"))

    def test_unknown_observation_field_is_rejected(self):
        snapshot = self.base()
        snapshot["observations"]["neural_summary"] = copy.deepcopy(snapshot["observations"]["actor"])
        result = sg.validate(snapshot)
        self.assertEqual(result["reason"], "UNKNOWN_OBSERVATION_FIELDS")

    def test_replay_is_deterministic(self):
        snapshot = self.base()
        first = sg.validate(copy.deepcopy(snapshot))
        second = sg.validate(copy.deepcopy(snapshot))
        self.assertEqual(first, second)
        self.assertEqual(first["receipt_sha256"], second["receipt_sha256"])


if __name__ == "__main__":
    unittest.main()
