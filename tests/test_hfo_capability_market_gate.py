from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "hfo_capability_market_gate.py"
SPEC = importlib.util.spec_from_file_location("hfo_capability_market_gate", MODULE)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def job() -> dict:
    return {
        "job_id": "J-1",
        "objective_id": "OBJ-1",
        "exact_input_refs": ["sha256:x"],
        "acceptance_tests": ["A1"],
        "effect_ceiling": "E1",
        "max_cost": 1.0,
        "deadline_or_recheck": "2026-08-29T16:00:00Z",
        "privacy_class": "PUBLIC_SAFE",
        "mutable_workpiece_key": "book2:chapter1",
        "verification_class": "DISTINCT_VERIFIER",
        "market_eligible": True,
        "operator_selects_worker_manually": False,
        "allocation_mode": "CONTRACT_NET_TOP_K",
        "broadcast_to_all_neural_actors": False,
    }


def bid() -> dict:
    return {
        "bidder_actor_or_phenotype_id": "HFO_GEN137_THRUD",
        "exact_capability_id_and_version": "code.cloudflare.v1",
        "qualification_receipts": ["receipt:1"],
        "capability_qualification_state": "QUALIFIED",
        "proposed_carrier_class": "CODEX",
        "predicted_cost": 0.5,
        "predicted_latency": 30,
        "confidence": 0.8,
        "confidence_evidence_basis": "3 similar verified closures",
        "required_tools": ["git", "wrangler"],
        "required_effect_authority": "E1",
        "known_failure_scars": ["scope-escape"],
        "proposed_acceptance_route": "HRIST->REGINLEIF",
        "self_accepts_bid": False,
        "self_grants_lease": False,
    }


class JobGateTests(unittest.TestCase):
    def test_market_eligible_job_passes_with_contract_net(self) -> None:
        self.assertEqual(mod.evaluate_job({"job": job()})["state"], "ALLOW")

    def test_operator_cannot_be_manual_worker_router(self) -> None:
        j = job(); j["operator_selects_worker_manually"] = True
        result = mod.evaluate_job({"job": j})
        self.assertEqual(result["code"], "BLOCK_OPERATOR_MANUAL_WORKER_SELECTION")
        self.assertEqual(result["downstream_effect_budget"], 0)

    def test_neural_broadcast_is_denied(self) -> None:
        j = job(); j["broadcast_to_all_neural_actors"] = True
        self.assertEqual(mod.evaluate_job({"job": j})["code"], "BLOCK_NEURAL_BROADCAST_ALLOCATION")

    def test_market_bypass_is_denied(self) -> None:
        j = job(); j["allocation_mode"] = "TAO_PICKS_AGENT"
        self.assertEqual(mod.evaluate_job({"job": j})["code"], "BLOCK_CAPABILITY_MARKET_BYPASS")


class BidGateTests(unittest.TestCase):
    def test_qualified_bounded_bid_passes(self) -> None:
        self.assertEqual(mod.evaluate_bid({"job": job(), "bid": bid()})["state"], "ALLOW")

    def test_unqualified_capability_is_denied(self) -> None:
        b = bid(); b["qualification_receipts"] = []
        self.assertEqual(mod.evaluate_bid({"job": job(), "bid": b})["code"], "BLOCK_UNQUALIFIED_CAPABILITY_CLAIM")

    def test_bidder_cannot_self_award(self) -> None:
        b = bid(); b["self_grants_lease"] = True
        self.assertEqual(mod.evaluate_bid({"job": job(), "bid": b})["code"], "BLOCK_BIDDER_SELF_AWARD")

    def test_over_budget_bid_is_denied(self) -> None:
        b = bid(); b["predicted_cost"] = 2.0
        self.assertEqual(mod.evaluate_bid({"job": job(), "bid": b})["code"], "BLOCK_BID_OVER_JOB_BUDGET")


class SelectionGateTests(unittest.TestCase):
    def test_reginleif_can_select_one_qualified_winner(self) -> None:
        payload = {"selection": {
            "selector_actor_id": "HFO_GEN142_REGINLEIF",
            "winner_bid_ids": ["B1"],
            "same_mutable_workpiece": True,
            "selected_bid_is_qualified": True,
            "bidder_selected_itself": False,
        }}
        self.assertEqual(mod.evaluate_selection(payload)["state"], "ALLOW")

    def test_untrusted_selector_is_denied(self) -> None:
        payload = {"selection": {
            "selector_actor_id": "HFO_GEN137_THRUD",
            "winner_bid_ids": ["B1"],
            "same_mutable_workpiece": True,
            "selected_bid_is_qualified": True,
            "bidder_selected_itself": False,
        }}
        self.assertEqual(mod.evaluate_selection(payload)["code"], "BLOCK_UNTRUSTED_CAPABILITY_SELECTOR")

    def test_two_winners_same_workpiece_are_denied(self) -> None:
        payload = {"selection": {
            "selector_actor_id": "HFO_REFERENCE_MONITOR",
            "winner_bid_ids": ["B1", "B2"],
            "same_mutable_workpiece": True,
            "selected_bid_is_qualified": True,
            "bidder_selected_itself": False,
        }}
        self.assertEqual(mod.evaluate_selection(payload)["code"], "BLOCK_MULTIPLE_WINNERS_SAME_WORKPIECE")


class ScaleGateTests(unittest.TestCase):
    def test_population_growth_blocked_when_operator_pain_increases(self) -> None:
        payload = {"scale": {
            "current_population": 40,
            "proposed_population": 100,
            "baseline_operator_touches_per_verified_world_effect": 1.0,
            "current_operator_touches_per_verified_world_effect": 1.2,
            "admitted_operator_touch_ceiling": 1.0,
            "verified_world_effect_sample_size": 20,
        }}
        result = mod.evaluate_scale(payload)
        self.assertEqual(result["code"], "BLOCK_SCALE_OPERATOR_PAIN_NOT_IMPROVING")
        self.assertEqual(result["state"], "DENY")

    def test_population_growth_requires_real_world_effect_sample(self) -> None:
        payload = {"scale": {
            "current_population": 40,
            "proposed_population": 100,
            "baseline_operator_touches_per_verified_world_effect": 1.0,
            "current_operator_touches_per_verified_world_effect": 0.5,
            "admitted_operator_touch_ceiling": 1.0,
            "verified_world_effect_sample_size": 0,
        }}
        self.assertEqual(mod.evaluate_scale(payload)["code"], "BLOCK_SCALE_WITHOUT_WORLD_EFFECT_SAMPLE")

    def test_population_growth_candidate_passes_when_operator_pain_drops(self) -> None:
        payload = {"scale": {
            "current_population": 40,
            "proposed_population": 100,
            "baseline_operator_touches_per_verified_world_effect": 1.0,
            "current_operator_touches_per_verified_world_effect": 0.5,
            "admitted_operator_touch_ceiling": 1.0,
            "verified_world_effect_sample_size": 20,
        }}
        self.assertEqual(mod.evaluate_scale(payload)["state"], "ALLOW")


if __name__ == "__main__":
    unittest.main()
