#!/usr/bin/env python3
"""Fail-closed evidence gate for operational hexagonality.

This is an admission/falsification helper, not a router, scheduler, or state owner.
It answers one question: did multiple distinct carrier adapters close the same
bounded semantic job under the same verifier/ConsumerAck contract?
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "hfo.hexagonal-runtime-assay.v1"
RECEIPT_SCHEMA = "hfo.hexagonal-adapter-receipt.v1"
COMPLETION_SCHEMA = "hfo.sigrun.worker_completion.v1"
ZERO_MARGINAL = "ZERO_MARGINAL"


def hold(code: str, **detail: Any) -> tuple[int, dict[str, Any]]:
    return 1, {"decision": "HOLD", "verdict": code, **detail}


def evaluate(value: Any) -> tuple[int, dict[str, Any]]:
    if not isinstance(value, dict):
        return hold("ASSAY_OBJECT_REQUIRED")
    if value.get("schema") != SCHEMA:
        return hold("ASSAY_SCHEMA_REFUSED")
    job = value.get("job")
    receipts = value.get("receipts")
    if not isinstance(job, dict) or not isinstance(receipts, list):
        return hold("ASSAY_FIELDS_REQUIRED")

    required_job = (
        "job_sha256", "task_sha256", "capability_contract_sha256",
        "semantic_output_sha256", "verifier_id", "semantic_owner",
    )
    if any(not isinstance(job.get(k), str) or not job[k] for k in required_job):
        return hold("JOB_BINDING_REQUIRED")
    if job.get("semantic_owner") != "hfo-sigrun-va-r0":
        return hold("SEMANTIC_OWNER_REFUSED")
    if len(receipts) < 2:
        return hold("TWO_ADAPTER_RECEIPTS_REQUIRED", observed=len(receipts))

    required_receipt = (
        "adapter_id", "provider_id", "harness_id", "host_id", "job_sha256",
        "task_sha256", "capability_contract_sha256", "semantic_output_sha256",
        "completion_schema", "verifier_id", "verifier_receipt_sha256",
        "consumer_ack_sha256", "billing_class", "effect_ceiling",
    )
    providers: set[str] = set()
    adapters: set[str] = set()
    harnesses: set[str] = set()
    hosts: set[str] = set()

    for i, receipt in enumerate(receipts):
        if not isinstance(receipt, dict) or receipt.get("schema") != RECEIPT_SCHEMA:
            return hold("RECEIPT_SCHEMA_REFUSED", index=i)
        missing = [k for k in required_receipt if not isinstance(receipt.get(k), str) or not receipt[k]]
        if missing:
            return hold("RECEIPT_BINDING_REQUIRED", index=i, missing=missing)
        for key in ("job_sha256", "task_sha256", "capability_contract_sha256", "semantic_output_sha256", "verifier_id"):
            if receipt[key] != job[key]:
                return hold("RECEIPT_JOB_BINDING_MISMATCH", index=i, field=key)
        if receipt["completion_schema"] != COMPLETION_SCHEMA:
            return hold("COMPLETION_SCHEMA_REFUSED", index=i)
        if receipt["billing_class"] != ZERO_MARGINAL:
            return hold("BILLING_CLASS_REFUSED", index=i, billing_class=receipt["billing_class"])
        if receipt.get("terminal") is not True:
            return hold("TERMINAL_REQUIRED", index=i)
        if receipt.get("controller_observed") is not True:
            return hold("CONTROLLER_OBSERVATION_REQUIRED", index=i)
        if receipt.get("independent_verifier") is not True:
            return hold("INDEPENDENT_VERIFIER_REQUIRED", index=i)
        if receipt.get("tao_hot_loop_actions") != 0:
            return hold("TAO_HOT_LOOP_NOT_ZERO", index=i)
        providers.add(receipt["provider_id"])
        adapters.add(receipt["adapter_id"])
        harnesses.add(receipt["harness_id"])
        hosts.add(receipt["host_id"])

    if len(providers) < 2:
        return hold("DISTINCT_PROVIDER_REQUIRED", providers=sorted(providers))
    if len(adapters) < 2:
        return hold("DISTINCT_ADAPTER_REQUIRED", adapters=sorted(adapters))
    if len(harnesses) < 2:
        return hold("DISTINCT_HARNESS_REQUIRED", harnesses=sorted(harnesses))
    if value.get("require_distinct_hosts") is True and len(hosts) < 2:
        return hold("DISTINCT_HOST_REQUIRED", hosts=sorted(hosts))

    return 0, {
        "decision": "ADMIT",
        "verdict": "HEXAGONAL_RUNTIME_PASS",
        "provider_count": len(providers),
        "adapter_count": len(adapters),
        "harness_count": len(harnesses),
        "host_count": len(hosts),
        "job_sha256": job["job_sha256"],
        "semantic_output_sha256": job["semantic_output_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("assay")
    args = parser.parse_args()
    try:
        value = json.loads(Path(args.assay).read_text(encoding="utf-8"))
    except Exception as exc:
        code, out = hold("ASSAY_UNREADABLE", error_type=type(exc).__name__)
        print(json.dumps(out, sort_keys=True))
        return code
    code, out = evaluate(value)
    print(json.dumps(out, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
