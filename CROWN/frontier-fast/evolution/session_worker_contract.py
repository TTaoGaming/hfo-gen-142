#!/usr/bin/env python3
from __future__ import annotations
import hashlib, pathlib

ALLOWED = {
    "chatgpt_a", "chatgpt_b", "codex_subscription",
    "claude_subscription", "kimi_subscription",
}

class ContractHold(RuntimeError):
    pass

def file_sha256(path: str) -> str:
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def validate(job: dict, receipt: dict, artifact_path: str) -> dict:
    if job.get("schema") != "hfo.session-proposal-job.v1":
        raise ContractHold("JOB_SCHEMA_MISMATCH")
    if receipt.get("schema") != "hfo.session-proposal-receipt.v1":
        raise ContractHold("RECEIPT_SCHEMA_MISMATCH")
    if job.get("job_id") != receipt.get("job_id"):
        raise ContractHold("JOB_ID_MISMATCH")
    if job.get("provider_class") not in ALLOWED:
        raise ContractHold("PROVIDER_CLASS_REFUSED")
    if receipt.get("provider_class") != job.get("provider_class"):
        raise ContractHold("PROVIDER_RECEIPT_MISMATCH")
    if job.get("effect_ceiling") != "NONE" or receipt.get("effect_count") != 0:
        raise ContractHold("EFFECT_CEILING_VIOLATED")
    if receipt.get("session_secret_exported") is not False:
        raise ContractHold("SESSION_SECRET_BOUNDARY_VIOLATED")
    artifact = pathlib.Path(artifact_path)
    if not artifact.is_file() or artifact.is_symlink():
        raise ContractHold("ARTIFACT_MISSING_OR_SYMLINK")
    size = artifact.stat().st_size
    if size <= 0 or size > int(job.get("max_output_bytes", 0)):
        raise ContractHold("ARTIFACT_SIZE_REFUSED")
    digest = file_sha256(str(artifact))
    if receipt.get("artifact_sha256") != digest or receipt.get("artifact_bytes") != size:
        raise ContractHold("ARTIFACT_BINDING_MISMATCH")
    return {"decision": "ADMIT_STATIC_PROPOSAL", "job_id": job["job_id"],
            "provider_class": job["provider_class"], "artifact_sha256": digest,
            "trusted_fitness": None, "promotion": "HOLD_SHARED_EVALUATOR"}
