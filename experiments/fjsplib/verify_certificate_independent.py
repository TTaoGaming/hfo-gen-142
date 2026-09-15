#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

PIN = "7b3f6fb1384309bd4abca866fe3bef2993139b91"
ROOT = f"https://raw.githubusercontent.com/ScheduleOpt/benchmarks/{PIN}/flexible-jobshop"


def fetch(url: str):
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def fail(code: str, **extra):
    print(json.dumps({"verified": False, "code": code, **extra}, sort_keys=True))
    raise SystemExit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate_json")
    a = ap.parse_args()
    result = json.loads(Path(a.certificate_json).read_text(encoding="utf-8"))
    name = result.get("instance")
    if not isinstance(name, str):
        fail("INSTANCE_MISSING")

    inst, inst_sha = fetch(f"{ROOT}/instances/json/{name}.json")
    bks, bks_sha = fetch(f"{ROOT}/solutions/bks.json")
    row = next((x for x in bks if x["instance"] == name), None)
    if row is None:
        fail("BKS_INSTANCE_MISSING")
    if result.get("source_commit") != PIN:
        fail("SOURCE_COMMIT_MISMATCH", got=result.get("source_commit"))
    if result.get("instance_sha256") != inst_sha:
        fail("INSTANCE_HASH_MISMATCH", expected=inst_sha, got=result.get("instance_sha256"))
    if result.get("bks_sha256") != bks_sha:
        fail("BKS_HASH_MISMATCH", expected=bks_sha, got=result.get("bks_sha256"))

    eligible = defaultdict(dict)
    for x in inst["operations"]:
        op, machine, duration = int(x["operation"]), int(x["machine"]), int(x["duration"])
        eligible[op][machine] = duration
    cert = result.get("certificate")
    if not isinstance(cert, list):
        fail("CERTIFICATE_MISSING")
    seen = set()
    by_machine = defaultdict(list)
    records = {}
    for x in cert:
        try:
            op = int(x["operation"]); machine = int(x["machine"])
            start = int(x["start"]); end = int(x["end"]); duration = int(x["duration"])
        except Exception:
            fail("CERTIFICATE_ROW_INVALID", row=x)
        if op in seen:
            fail("DUPLICATE_OPERATION", operation=op)
        seen.add(op)
        if op not in eligible:
            fail("UNKNOWN_OPERATION", operation=op)
        if machine not in eligible[op]:
            fail("INELIGIBLE_MACHINE", operation=op, machine=machine)
        expected_duration = eligible[op][machine]
        if duration != expected_duration:
            fail("DURATION_MISMATCH", operation=op, machine=machine,
                 expected=expected_duration, got=duration)
        if start < 0 or end != start + duration:
            fail("TIME_MISMATCH", operation=op, start=start, end=end, duration=duration)
        rec = {"operation": op, "machine": machine, "start": start, "end": end, "duration": duration}
        records[op] = rec
        by_machine[machine].append(rec)
    expected_ops = set(eligible)
    if seen != expected_ops:
        fail("OPERATION_SET_MISMATCH", missing=sorted(expected_ops - seen), extra=sorted(seen - expected_ops))

    for e in inst["precedences"]:
        before, after = int(e["before"]), int(e["after"])
        if records[before]["end"] > records[after]["start"]:
            fail("PRECEDENCE_VIOLATION", before=before, after=after,
                 before_end=records[before]["end"], after_start=records[after]["start"])

    for machine, rows in by_machine.items():
        rows.sort(key=lambda z: (z["start"], z["end"], z["operation"]))
        for left, right in zip(rows, rows[1:]):
            if left["end"] > right["start"]:
                fail("MACHINE_OVERLAP", machine=machine,
                     left=left["operation"], right=right["operation"],
                     left_end=left["end"], right_start=right["start"])

    makespan = max(x["end"] for x in records.values())
    if int(result.get("makespan", -1)) != makespan:
        fail("MAKESPAN_MISMATCH", recomputed=makespan, reported=result.get("makespan"))
    canonical = json.dumps(sorted(cert, key=lambda x: int(x["operation"])), separators=(",", ":"), sort_keys=True)
    cert_sha = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps({
        "verified": True,
        "code": "CERTIFICATE_FEASIBLE",
        "instance": name,
        "source_commit": PIN,
        "instance_sha256": inst_sha,
        "bks_sha256": bks_sha,
        "certificate_sha256": cert_sha,
        "operations": len(records),
        "machines_used": len(by_machine),
        "makespan": makespan,
        "published_lb": int(row["lower_bound"]),
        "published_ub": int(row["upper_bound"]),
        "matches_public_ub": makespan == int(row["upper_bound"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
