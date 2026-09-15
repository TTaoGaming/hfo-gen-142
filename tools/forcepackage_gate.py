#!/usr/bin/env python3
"""Pure deterministic admission/compiler for HFO ForcePackage v1.

This is a forcing function, not a scheduler, queue, dispatcher, state owner, or
authority owner. It turns one versioned package into stable actor intents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "hfo.forcepackage.v1"
OUT_SCHEMA = "hfo.forcepackage-admission.v1"
ACTOR_INTENT_SCHEMA = "hfo.actor-intent.v1"
POLICY = "forcepackage-gate-v1"
SEMANTIC_OWNER = "hfo-sigrun-va-r0"
RECEIPT_SINK = "github:TTaoGaming/hfo-gen-142#13"

# Worker/verification phenotypes currently defined in ZERG_CAPACITY_ARCHETYPES.md.
# HYDRA/ULTRALISK remain voice handles until their engineering contracts are versioned.
WORKER_ARCHETYPES = {
    "LING", "TWINLING", "ROACH", "RED_QUEEN", "REDUCER", "VERIFIER", "EXTRACTOR",
}
HUMAN_BOUNDARIES = {
    "secret", "oauth", "2fa", "payment", "permission",
    "protected_merge", "irreversible_external_submit",
}
PACKAGE_KEYS = {
    "schema", "package_id", "mission_id", "root_actor_id", "domain", "domain_explicit",
    "intent", "fitness", "verifier", "deadline_utc", "max_runtime_minutes", "max_attempts",
    "max_spend_usd", "effect_ceiling", "receipt_sink", "semantic_owner",
    "provider_policy", "human_boundaries", "control_plane", "tao_relay_required",
    "consumer_ack_required", "stop_conditions", "max_children", "max_concurrency",
    "formations",
}
FORMATION_KEYS = {
    "formation_id", "archetype", "count", "intent", "required_skill",
    "verifier_formation_id", "max_attempts_each", "max_spend_usd_each",
    "effect_ceiling",
}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{1,127}$")


class Refused(ValueError):
    def __init__(self, verdict: str, **detail: Any):
        super().__init__(verdict)
        self.verdict = verdict
        self.detail = detail


def refuse(verdict: str, **detail: Any) -> None:
    raise Refused(verdict, **detail)


def canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value: Any) -> str:
    text = value if isinstance(value, str) else canon(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def strict_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def exact_object(value: Any, expected: set[str], verdict: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        refuse(f"{verdict}_TYPE")
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing or extra:
        refuse(verdict, missing=missing, extra=extra)
    return value


def parse_utc(value: Any) -> datetime:
    if not isinstance(value, str):
        refuse("DEADLINE_INVALID")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        refuse("DEADLINE_INVALID")


def normalized_package(package: dict[str, Any]) -> dict[str, Any]:
    out = dict(package)
    out["human_boundaries"] = sorted(package["human_boundaries"])
    out["stop_conditions"] = sorted(package["stop_conditions"])
    out["formations"] = sorted(
        [dict(row) for row in package["formations"]], key=lambda row: row["formation_id"]
    )
    return out


def validate_package(package: Any, now: datetime | None = None) -> dict[str, Any]:
    p = exact_object(package, PACKAGE_KEYS, "PACKAGE_FIELDS_REFUSED")
    if p.get("schema") != SCHEMA:
        refuse("PACKAGE_SCHEMA_REFUSED", declared=p.get("schema"))

    for key in ("package_id", "mission_id"):
        value = p.get(key)
        if not isinstance(value, str) or not ID_RE.fullmatch(value):
            refuse("PACKAGE_ID_REFUSED", field=key)
    if not isinstance(p.get("root_actor_id"), str) or not p["root_actor_id"].strip():
        refuse("ROOT_ACTOR_ID_REQUIRED")

    domain = p.get("domain")
    if not isinstance(domain, str) or not domain.strip():
        refuse("DOMAIN_REQUIRED")
    if p.get("domain_explicit") is not True and domain.lower() != "domain_agnostic":
        refuse("BLOCKED_DOMAIN_PROXY", declared_domain=domain)
    if not isinstance(p.get("intent"), str) or not p["intent"].strip():
        refuse("INTENT_REQUIRED")

    fitness = exact_object(p.get("fitness"), {"primary", "external_verification_required"}, "FITNESS_FIELDS_REFUSED")
    if not isinstance(fitness.get("primary"), str) or not fitness["primary"].strip():
        refuse("FITNESS_REQUIRED")
    if fitness.get("external_verification_required") is not True:
        refuse("EXTERNAL_VERIFICATION_REQUIRED")

    verifier = exact_object(p.get("verifier"), {"id", "frozen"}, "VERIFIER_POLICY_FIELDS_REFUSED")
    if not isinstance(verifier.get("id"), str) or not verifier["id"].strip():
        refuse("VERIFIER_REQUIRED")
    if verifier.get("frozen") is not True:
        refuse("VERIFIER_NOT_FROZEN")

    now = now or datetime.now(timezone.utc)
    if parse_utc(p.get("deadline_utc")) <= now:
        refuse("DEADLINE_EXPIRED", deadline_utc=p.get("deadline_utc"))

    runtime = p.get("max_runtime_minutes")
    attempts = p.get("max_attempts")
    spend = p.get("max_spend_usd")
    if not strict_int(runtime) or not 1 <= runtime <= 1440:
        refuse("RUNTIME_BOUND_INVALID", max_runtime_minutes=runtime)
    if not strict_int(attempts) or not 1 <= attempts <= 2048:
        refuse("ATTEMPT_BOUND_INVALID", max_attempts=attempts)
    if not isinstance(spend, (int, float)) or isinstance(spend, bool) or spend < 0:
        refuse("SPEND_BOUND_INVALID", max_spend_usd=spend)

    effect = p.get("effect_ceiling")
    if not isinstance(effect, str) or not effect.strip():
        refuse("EFFECT_CEILING_REQUIRED")
    if p.get("receipt_sink") != RECEIPT_SINK:
        refuse("RENDEZVOUS_MISMATCH", required=RECEIPT_SINK)
    if p.get("semantic_owner") != SEMANTIC_OWNER:
        refuse("DUPLICATE_SEMANTIC_OWNER", required=SEMANTIC_OWNER)

    provider = exact_object(
        p.get("provider_policy"), {"role", "frontier_required", "allow_local_fallback"},
        "PROVIDER_POLICY_FIELDS_REFUSED",
    )
    if provider.get("role") != "leaf":
        refuse("PROVIDER_NOT_LEAF")
    if not isinstance(provider.get("frontier_required"), bool) or not isinstance(provider.get("allow_local_fallback"), bool):
        refuse("PROVIDER_POLICY_TYPE")
    if provider["frontier_required"] and provider["allow_local_fallback"]:
        refuse("BLOCKED_PROVIDER_FALLBACK")

    boundaries = p.get("human_boundaries")
    if not isinstance(boundaries, list) or not all(isinstance(x, str) for x in boundaries):
        refuse("HUMAN_BOUNDARY_INVALID")
    if len(boundaries) != len(set(boundaries)) or any(x not in HUMAN_BOUNDARIES for x in boundaries):
        refuse("HUMAN_BOUNDARY_INVALID")
    if p.get("tao_relay_required") is not False:
        refuse("TAO_RELAY_NOT_RUNTIME_CONTINUATION")

    control = exact_object(
        p.get("control_plane"), {"new_control_plane", "recover_probe_repair_completed"},
        "CONTROL_PLANE_FIELDS_REFUSED",
    )
    if control.get("new_control_plane") is not False:
        refuse("BLOCKED_NEW_CONTROL_PLANE")
    if control.get("recover_probe_repair_completed") is not True:
        refuse("RECOVER_PROBE_REPAIR_FIRST")
    if p.get("consumer_ack_required") is not True:
        refuse("CONSUMER_ACK_REQUIRED")

    stops = p.get("stop_conditions")
    if not isinstance(stops, list) or not stops or not all(isinstance(x, str) and x.strip() for x in stops):
        refuse("STOP_CONDITIONS_REQUIRED")

    max_children = p.get("max_children")
    max_concurrency = p.get("max_concurrency")
    if not strict_int(max_children) or not 2 <= max_children <= 128:
        refuse("MAX_CHILDREN_INVALID", max_children=max_children)
    if not strict_int(max_concurrency) or not 1 <= max_concurrency <= max_children:
        refuse("MAX_CONCURRENCY_INVALID", max_concurrency=max_concurrency)

    formations = p.get("formations")
    if not isinstance(formations, list) or not formations:
        refuse("FORMATIONS_REQUIRED")

    ids: set[str] = set()
    rows: list[dict[str, Any]] = []
    total_children = 0
    total_attempts = 0
    total_spend = 0.0
    for raw in formations:
        f = exact_object(raw, FORMATION_KEYS, "FORMATION_FIELDS_REFUSED")
        fid = f.get("formation_id")
        if not isinstance(fid, str) or not ID_RE.fullmatch(fid) or fid in ids:
            refuse("FORMATION_ID_REFUSED", formation_id=fid)
        ids.add(fid)

        archetype = f.get("archetype")
        if not isinstance(archetype, str) or archetype not in WORKER_ARCHETYPES:
            refuse("ARCHETYPE_UNVERSIONED", formation_id=fid, archetype=archetype)
        count = f.get("count")
        if not strict_int(count) or not 1 <= count <= 128:
            refuse("FORMATION_COUNT_INVALID", formation_id=fid, count=count)
        if not isinstance(f.get("intent"), str) or not f["intent"].strip():
            refuse("FORMATION_INTENT_REQUIRED", formation_id=fid)
        skill = f.get("required_skill")
        if skill is not None and (not isinstance(skill, str) or not skill.strip()):
            refuse("FORMATION_SKILL_INVALID", formation_id=fid)
        each_attempts = f.get("max_attempts_each")
        each_spend = f.get("max_spend_usd_each")
        if not strict_int(each_attempts) or not 1 <= each_attempts <= 20:
            refuse("FORMATION_ATTEMPT_BOUND_INVALID", formation_id=fid)
        if not isinstance(each_spend, (int, float)) or isinstance(each_spend, bool) or each_spend < 0:
            refuse("FORMATION_SPEND_BOUND_INVALID", formation_id=fid)
        if f.get("effect_ceiling") != effect:
            refuse("CHILD_EFFECT_CEILING_MISMATCH", formation_id=fid)
        if archetype == "VERIFIER":
            if f.get("verifier_formation_id") is not None:
                refuse("VERIFIER_RECURSION_REFUSED", formation_id=fid)
        elif not isinstance(f.get("verifier_formation_id"), str):
            refuse("VERIFIER_FORMATION_REQUIRED", formation_id=fid)

        total_children += count
        total_attempts += count * each_attempts
        total_spend += count * float(each_spend)
        rows.append(f)

    if total_children < 2 or total_children > max_children:
        refuse("CHILD_COUNT_BOUND", total_children=total_children, max_children=max_children)
    if max_concurrency > total_children:
        refuse("MAX_CONCURRENCY_EXCEEDS_CHILDREN", max_concurrency=max_concurrency, total_children=total_children)
    if total_attempts > attempts:
        refuse("PACKAGE_ATTEMPT_BUDGET_EXCEEDED", required=total_attempts, max_attempts=attempts)
    if total_spend > float(spend) + 1e-9:
        refuse("PACKAGE_SPEND_BUDGET_EXCEEDED", required=round(total_spend, 10), max_spend_usd=spend)

    by_id = {f["formation_id"]: f for f in rows}
    verifier_ids = {f["formation_id"] for f in rows if f["archetype"] == "VERIFIER"}
    if not verifier_ids:
        refuse("INDEPENDENT_VERIFIER_REQUIRED")
    for f in rows:
        if f["archetype"] == "VERIFIER":
            continue
        vf = f["verifier_formation_id"]
        if vf == f["formation_id"]:
            refuse("SELF_VERIFICATION_REFUSED", formation_id=f["formation_id"])
        if vf not in by_id:
            refuse("VERIFIER_FORMATION_UNKNOWN", formation_id=f["formation_id"], verifier_formation_id=vf)
        if by_id[vf]["archetype"] != "VERIFIER":
            refuse("VERIFIER_FORMATION_NOT_VERIFIER", formation_id=f["formation_id"], verifier_formation_id=vf)

    return normalized_package(p)


def compile_actor_intents(package: dict[str, Any]) -> dict[str, Any]:
    normalized = validate_package(package)
    package_sha = sha256(normalized)
    root = normalized["root_actor_id"]
    actors_by_formation: dict[str, list[str]] = {}
    for f in normalized["formations"]:
        actors_by_formation[f["formation_id"]] = [
            f"{root}/fp/{normalized['package_id']}@{package_sha[:12]}/{f['formation_id']}/{i:03d}"
            for i in range(1, f["count"] + 1)
        ]

    intents: list[dict[str, Any]] = []
    for f in normalized["formations"]:
        verifier_actor_ids = [] if f["archetype"] == "VERIFIER" else actors_by_formation[f["verifier_formation_id"]]
        for ordinal, actor_id in enumerate(actors_by_formation[f["formation_id"]], 1):
            seed = {"package_sha256": package_sha, "formation_id": f["formation_id"], "ordinal": ordinal, "actor_id": actor_id}
            intents.append({
                "schema": ACTOR_INTENT_SCHEMA,
                "intent_id": sha256(seed),
                "package_id": normalized["package_id"],
                "package_sha256": package_sha,
                "mission_id": normalized["mission_id"],
                "actor_id": actor_id,
                "parent_actor_id": root,
                "formation_id": f["formation_id"],
                "ordinal": ordinal,
                "archetype": f["archetype"],
                "package_intent": normalized["intent"],
                "intent": f["intent"],
                "domain": normalized["domain"],
                "domain_explicit": normalized["domain_explicit"],
                "fitness": normalized["fitness"],
                "verifier": normalized["verifier"],
                "deadline_utc": normalized["deadline_utc"],
                "max_runtime_minutes": normalized["max_runtime_minutes"],
                "provider_policy": normalized["provider_policy"],
                "human_boundaries": normalized["human_boundaries"],
                "stop_conditions": normalized["stop_conditions"],
                "consumer_ack_required": normalized["consumer_ack_required"],
                "promotion": {"requested": False},
                "required_skill": f["required_skill"],
                "verifier_actor_ids": verifier_actor_ids,
                "max_attempts": f["max_attempts_each"],
                "max_spend_usd": f["max_spend_usd_each"],
                "effect_ceiling": f["effect_ceiling"],
                "semantic_owner": normalized["semantic_owner"],
                "receipt_sink": normalized["receipt_sink"],
                "carrier_id": None,
                "provider_binding": None,
                "status": "DESIRED_NOT_CLAIMED",
            })

    out = {
        "schema": OUT_SCHEMA,
        "policy_version": POLICY,
        "decision": "ADMIT",
        "transition": "EMIT_TO_PACKAGE_ADMISSION",
        "acceptance_scope": "PACKAGE_SCHEMA_POLICY_ONLY",
        "execution_status": "NOT_DISPATCHED",
        "package_id": normalized["package_id"],
        "mission_id": normalized["mission_id"],
        "package_sha256": package_sha,
        "actor_intents": intents,
        "actor_intents_sha256": sha256(intents),
        "child_count": len(intents),
        "max_concurrency": normalized["max_concurrency"],
        "package_constraints": {
            "deadline_utc": normalized["deadline_utc"],
            "max_runtime_minutes": normalized["max_runtime_minutes"],
            "max_attempts": normalized["max_attempts"],
            "max_spend_usd": normalized["max_spend_usd"],
            "effect_ceiling": normalized["effect_ceiling"],
            "stop_conditions": normalized["stop_conditions"],
            "human_boundaries": normalized["human_boundaries"],
        },
        "semantic_owner": normalized["semantic_owner"],
        "receipt_sink": normalized["receipt_sink"],
        "verifier_independence_status": "REQUIRES_DOWNSTREAM_CAPABILITY_BINDING",
        "next_contract": "MATERIALIZE_ACTOR_INTENTS_TO_EXISTING_WORKITEM_RUNTIME_AND_SEMANTIC_CLAIM",
    }
    out["admission_sha256"] = sha256(out)
    return out


def hold_packet(package: Any, exc: Refused) -> dict[str, Any]:
    package_id = package.get("package_id") if isinstance(package, dict) else None
    out = {
        "schema": OUT_SCHEMA,
        "policy_version": POLICY,
        "decision": "HOLD",
        "transition": "EMIT_REJECTED",
        "execution_status": "NOT_DISPATCHED",
        "package_id": package_id,
        "verdict": exc.verdict,
        "detail": exc.detail,
    }
    out["admission_sha256"] = sha256(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--output")
    args = ap.parse_args()
    try:
        package = json.loads(Path(args.package).read_text(encoding="utf-8"))
    except Exception as exc:
        packet = hold_packet(None, Refused("PACKAGE_UNREADABLE", error=type(exc).__name__))
        print(json.dumps(packet, sort_keys=True))
        return 1
    try:
        packet = compile_actor_intents(package)
        rc = 0
    except Refused as exc:
        packet = hold_packet(package, exc)
        rc = 1
    if args.output:
        Path(args.output).write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(packet, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
