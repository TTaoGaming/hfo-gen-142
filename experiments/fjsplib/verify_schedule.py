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


def fetch_json(url: str):
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def fail(msg: str):
    raise SystemExit("VERIFY_FAIL: " + msg)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate")
    a = ap.parse_args()
    result = json.loads(Path(a.certificate).read_text(encoding="utf-8"))
    if "certificate" not in result:
        print("NO_CERTIFICATE")
        return 0

    name = result["instance"]
    inst, inst_sha = fetch_json(f"{ROOT}/instances/json/{name}.json")
    bks, bks_sha = fetch_json(f"{ROOT}/solutions/bks.json")
    row = next(x for x in bks if x["instance"] == name)
    if result.get("source_commit") != PIN or result.get("instance_sha256") != inst_sha or result.get("bks_sha256") != bks_sha:
        fail("source binding mismatch")

    allowed = defaultdict(dict)
    for x in inst["operations"]:
        allowed[int(x["operation"])][int(x["machine"])] = int(x["duration"])
    cert = result["certificate"]
    if len(cert) != len(allowed):
        fail(f"operation count {len(cert)} != {len(allowed)}")
    by_op = {int(x["operation"]): x for x in cert}
    if set(by_op) != set(allowed):
        fail("operation id set mismatch")

    by_machine = defaultdict(list)
    for op, x in by_op.items():
        m, s, e, d = int(x["machine"]), int(x["start"]), int(x["end"]), int(x["duration"])
        if m not in allowed[op]:
            fail(f"op {op} illegal machine {m}")
        if d != allowed[op][m] or e - s != d or s < 0:
            fail(f"op {op} duration/time mismatch")
        by_machine[m].append((s, e, op))

    for edge in inst["precedences"]:
        b, c = int(edge["before"]), int(edge["after"])
        if int(by_op[b]["end"]) > int(by_op[c]["start"]):
            fail(f"precedence {b}->{c} violated")

    for m, xs in by_machine.items():
        xs.sort()
        for i in range(1, len(xs)):
            if xs[i - 1][1] > xs[i][0]:
                fail(f"machine {m} overlap: {xs[i-1]} vs {xs[i]}")

    makespan = max(int(x["end"]) for x in cert)
    if makespan != int(result["makespan"]):
        fail("reported makespan mismatch")
    published_ub = int(row["upper_bound"])
    published_lb = int(row["lower_bound"])
    if makespan >= published_ub:
        fail(f"not an improvement: {makespan} >= {published_ub}")

    verdict = {
        "schema": "hfo.fjsplib-certificate-verdict.v1",
        "instance": name,
        "verdict": "PASS",
        "makespan": makespan,
        "published_lb": published_lb,
        "published_ub": published_ub,
        "improvement": published_ub - makespan,
        "closes_gap": makespan <= published_lb,
        "source_commit": PIN,
        "instance_sha256": inst_sha,
        "bks_sha256": bks_sha,
    }
    Path(a.certificate + ".verified.json").write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(verdict, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
