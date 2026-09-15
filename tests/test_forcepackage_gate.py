import copy
import json
import unittest
from datetime import datetime, timedelta, timezone

from tools.forcepackage_gate import Refused, compile_actor_intents


def base_package():
    return {
        "schema": "hfo.forcepackage.v1",
        "package_id": "FP-VOICE-R0-001",
        "mission_id": "MISSION-VOICE-R0-001",
        "root_actor_id": "SIGRUN/C2",
        "domain": "domain_agnostic",
        "domain_explicit": False,
        "intent": "Test voice-to-swarm package admission without dispatch.",
        "fitness": {
            "primary": "externally_verified_useful_progress_per_operator_minute",
            "external_verification_required": True,
        },
        "verifier": {"id": "forcepackage-r0-frozen-assay", "frozen": True},
        "deadline_utc": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "max_runtime_minutes": 60,
        "max_attempts": 6,
        "max_spend_usd": 3.0,
        "effect_ceiling": "NO_EXTERNAL_EFFECT",
        "receipt_sink": "github:TTaoGaming/hfo-gen-142#13",
        "semantic_owner": "hfo-sigrun-va-r0",
        "provider_policy": {
            "role": "leaf",
            "frontier_required": False,
            "allow_local_fallback": False,
        },
        "human_boundaries": [],
        "control_plane": {
            "new_control_plane": False,
            "recover_probe_repair_completed": True,
        },
        "tao_relay_required": False,
        "consumer_ack_required": True,
        "stop_conditions": ["deadline", "budget", "verifier_failure"],
        "max_children": 8,
        "max_concurrency": 3,
        "formations": [
            {
                "formation_id": "research",
                "archetype": "LING",
                "count": 2,
                "intent": "Gather bounded evidence.",
                "required_skill": None,
                "verifier_formation_id": "verify",
                "max_attempts_each": 1,
                "max_spend_usd_each": 0.5,
                "effect_ceiling": "NO_EXTERNAL_EFFECT",
            },
            {
                "formation_id": "verify",
                "archetype": "VERIFIER",
                "count": 1,
                "intent": "Independently verify child evidence.",
                "required_skill": None,
                "verifier_formation_id": None,
                "max_attempts_each": 1,
                "max_spend_usd_each": 0.5,
                "effect_ceiling": "NO_EXTERNAL_EFFECT",
            },
        ],
    }


class ForcePackageGateTests(unittest.TestCase):
    def verdict(self, package):
        with self.assertRaises(Refused) as ctx:
            compile_actor_intents(package)
        return ctx.exception.verdict

    def test_valid_package_admits_but_does_not_dispatch(self):
        out = compile_actor_intents(base_package())
        self.assertEqual("ADMIT", out["decision"])
        self.assertEqual("PACKAGE_SCHEMA_POLICY_ONLY", out["acceptance_scope"])
        self.assertEqual("NOT_DISPATCHED", out["execution_status"])
        self.assertEqual(3, out["child_count"])
        self.assertEqual(
            "MATERIALIZE_ACTOR_INTENTS_TO_EXISTING_WORKITEM_RUNTIME_AND_SEMANTIC_CLAIM",
            out["next_contract"],
        )
        self.assertTrue(all(x["carrier_id"] is None for x in out["actor_intents"]))
        self.assertTrue(all(x["status"] == "DESIRED_NOT_CLAIMED" for x in out["actor_intents"]))

    def test_reordering_formations_and_sets_is_deterministic(self):
        a = base_package()
        b = copy.deepcopy(a)
        b["formations"] = list(reversed(b["formations"]))
        b["stop_conditions"] = list(reversed(b["stop_conditions"]))
        out_a = compile_actor_intents(a)
        out_b = compile_actor_intents(b)
        self.assertEqual(out_a["package_sha256"], out_b["package_sha256"])
        self.assertEqual(out_a["actor_intents_sha256"], out_b["actor_intents_sha256"])
        self.assertEqual(out_a["admission_sha256"], out_b["admission_sha256"])

    def test_unknown_top_level_field_fails_closed(self):
        p = base_package()
        p["carrier_id"] = "provider:made-up"
        self.assertEqual("PACKAGE_FIELDS_REFUSED", self.verdict(p))

    def test_undefined_hydra_is_refused_until_versioned(self):
        p = base_package()
        p["formations"][0]["archetype"] = "HYDRA"
        self.assertEqual("ARCHETYPE_UNVERSIONED", self.verdict(p))

    def test_no_verifier_is_refused(self):
        p = base_package()
        p["formations"] = [p["formations"][0]]
        p["formations"][0]["verifier_formation_id"] = "missing"
        p["max_concurrency"] = 2
        self.assertEqual("INDEPENDENT_VERIFIER_REQUIRED", self.verdict(p))

    def test_verifier_reference_must_exist(self):
        p = base_package()
        p["formations"][0]["verifier_formation_id"] = "absent"
        self.assertEqual("VERIFIER_FORMATION_UNKNOWN", self.verdict(p))

    def test_verifier_reference_must_point_to_verifier(self):
        p = base_package()
        p["formations"].append({
            "formation_id": "gather2",
            "archetype": "LING",
            "count": 1,
            "intent": "Second gatherer.",
            "required_skill": None,
            "verifier_formation_id": "verify",
            "max_attempts_each": 1,
            "max_spend_usd_each": 0.1,
            "effect_ceiling": "NO_EXTERNAL_EFFECT",
        })
        p["formations"][0]["verifier_formation_id"] = "gather2"
        self.assertEqual("VERIFIER_FORMATION_NOT_VERIFIER", self.verdict(p))

    def test_verifier_cannot_require_recursive_verifier(self):
        p = base_package()
        p["formations"][1]["verifier_formation_id"] = "verify"
        self.assertEqual("VERIFIER_RECURSION_REFUSED", self.verdict(p))

    def test_boolean_count_is_refused(self):
        p = base_package()
        p["formations"][0]["count"] = True
        self.assertEqual("FORMATION_COUNT_INVALID", self.verdict(p))

    def test_budget_overflow_fails_closed(self):
        p = base_package()
        p["max_spend_usd"] = 0.9
        self.assertEqual("PACKAGE_SPEND_BUDGET_EXCEEDED", self.verdict(p))

    def test_attempt_overflow_fails_closed(self):
        p = base_package()
        p["max_attempts"] = 2
        self.assertEqual("PACKAGE_ATTEMPT_BUDGET_EXCEEDED", self.verdict(p))

    def test_effect_ceiling_cannot_be_widened_by_child(self):
        p = base_package()
        p["formations"][0]["effect_ceiling"] = "WRITE"
        self.assertEqual("CHILD_EFFECT_CEILING_MISMATCH", self.verdict(p))

    def test_new_control_plane_is_refused(self):
        p = base_package()
        p["control_plane"]["new_control_plane"] = True
        self.assertEqual("BLOCKED_NEW_CONTROL_PLANE", self.verdict(p))

    def test_wrong_semantic_owner_is_refused(self):
        p = base_package()
        p["semantic_owner"] = "chat-memory"
        self.assertEqual("DUPLICATE_SEMANTIC_OWNER", self.verdict(p))

    def test_frozen_verifier_is_required(self):
        p = base_package()
        p["verifier"]["frozen"] = False
        self.assertEqual("VERIFIER_NOT_FROZEN", self.verdict(p))

    def test_actor_intent_carries_materialization_constraints(self):
        p = base_package()
        out = compile_actor_intents(p)
        actor = out["actor_intents"][0]
        self.assertEqual(p["deadline_utc"], actor["deadline_utc"])
        self.assertEqual(p["fitness"], actor["fitness"])
        self.assertEqual(p["verifier"], actor["verifier"])
        self.assertEqual(p["provider_policy"], actor["provider_policy"])
        self.assertEqual(sorted(p["stop_conditions"]), actor["stop_conditions"])
        self.assertEqual({"requested": False}, actor["promotion"])

    def test_expired_package_is_refused(self):
        p = base_package()
        p["deadline_utc"] = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        self.assertEqual("DEADLINE_EXPIRED", self.verdict(p))

    def test_concurrency_cannot_exceed_materialized_children(self):
        p = base_package()
        p["max_concurrency"] = 4
        self.assertEqual("MAX_CONCURRENCY_EXCEEDS_CHILDREN", self.verdict(p))

    def test_work_children_receive_distinct_verifier_actor_ids(self):
        out = compile_actor_intents(base_package())
        research = [x for x in out["actor_intents"] if x["formation_id"] == "research"]
        verifiers = [x for x in out["actor_intents"] if x["formation_id"] == "verify"]
        self.assertEqual(1, len(verifiers))
        self.assertEqual([verifiers[0]["actor_id"]], research[0]["verifier_actor_ids"])
        self.assertNotEqual(research[0]["actor_id"], verifiers[0]["actor_id"])

    def test_output_has_no_success_or_consumer_ack_claim(self):
        out = compile_actor_intents(base_package())
        raw = json.dumps(out, sort_keys=True)
        self.assertNotIn('"SUCCESS"', raw)
        self.assertNotIn('"consumer_ack":', raw.lower())


if __name__ == "__main__":
    unittest.main()
