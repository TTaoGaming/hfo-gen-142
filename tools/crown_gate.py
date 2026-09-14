#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

PRESTIGE_FIELDS = (
    "independent_verifier",
    "public_attribution",
    "real_incumbent_competition",
    "buyer_mapping",
    "durable_public_evidence",
    "accepted_submission_protocol",
)
FRONTIER_CLASSES = {
    "frontier",
    "frontier_api",
    "frontier_subscription_bridge",
}

def reject(verdict, **detail):
    print(json.dumps({"decision": "HOLD", "verdict": verdict, **detail}, sort_keys=True))
    return 1

def evaluate(candidate):
    missing = [k for k in PRESTIGE_FIELDS if candidate.get(k) is not True]
    if missing:
        return reject("KILL_PROXY", missing=missing)
    if candidate.get("frontier_required") is True:
        if candidate.get("provider_live") is not True:
            return reject("BLOCKED_PROVIDER_AUTH")
        if candidate.get("provider_class") not in FRONTIER_CLASSES:
            return reject("BLOCKED_PROVIDER_CLASS")

    if candidate.get("crown_won") is True:
        proof = (
            candidate.get("public_result") is True
            and candidate.get("accepted_protocol_result") is True
            and candidate.get("beats_incumbent") is True
        )
        if not proof:
            return reject("REJECT_UNPROVEN_CROWN")

    print(json.dumps({"decision": "ADMIT", "verdict": "ADMIT"}, sort_keys=True))
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate")
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    return evaluate(candidate)

if __name__ == "__main__":
    raise SystemExit(main())
