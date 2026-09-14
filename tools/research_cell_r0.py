#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, html, json, re, urllib.request
from pathlib import Path

UA = "GEN142-research-cell-r0/1.0"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        body = r.read()
        return body, r.headers.get("content-type", "")


def textify(body: bytes) -> str:
    s = body.decode("utf-8", errors="replace")
    s = re.sub(r"<script\b[^>]*>.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style\b[^>]*>.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("outdir")
    args = ap.parse_args()
    task_path = Path(args.task)
    task = json.loads(task_path.read_text(encoding="utf-8"))
    if task.get("schema") != "hfo.research-workitem.v1":
        raise SystemExit("TASK_SCHEMA_REFUSED")
    out = Path(args.outdir); out.mkdir(parents=True, exist_ok=True)
    spec_sha = sha256(task_path.read_bytes())

    health_raw, _ = fetch(task["cloudflare_health_url"])
    health = json.loads(health_raw.decode())
    if health.get("ok") is not True:
        raise SystemExit("CLOUDFLARE_HEALTH_REFUSED")

    sources = []
    for src in task["sources"]:
        raw, ctype = fetch(src["url"])
        txt = textify(raw)
        missing = [x for x in src["assertions"] if x.lower() not in txt.lower()]
        sources.append({
            "url": src["url"], "sha256": sha256(raw), "content_type": ctype,
            "assertions": src["assertions"], "missing": missing,
        })
    passed = all(not x["missing"] for x in sources)
    result = {
        "schema": "hfo.research-cell-result.v1", "work_id": task["work_id"],
        "spec_sha256": spec_sha, "verdict": "PASS" if passed else "FAIL",
        "question": task["question"], "cloudflare_health": health,
        "sources": sources, "next_state": "RETIRE" if passed else "HOLD",
        "tao_hot_loop_actions": 0,
    }
    result_bytes = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["result_sha256"] = sha256(result_bytes)
    (out / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        f"## RESEARCH CELL R0 — {result['verdict']}", "",
        f"- WorkItem: `{task['work_id']}`", f"- Question: {task['question']}",
        f"- Cloudflare actor health: `{health}`", f"- Spec SHA256: `{spec_sha}`",
        f"- Result SHA256: `{result['result_sha256']}`", "",
        "### Tool-observed evidence",
    ]
    for src in sources:
        lines += [f"- {src['url']}", f"  - body SHA256 `{src['sha256']}`", f"  - assertions missing: `{src['missing']}`"]
    lines += ["", f"**Disposition:** `{result['next_state']}`. This cell owns no scheduler/queue/lease; it is a bounded research worker with a durable GitHub ConsumerAck."]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "work_id": task["work_id"], "spec_sha256": spec_sha, "result_sha256": result["result_sha256"]}))
    return 0 if passed else 2

if __name__ == "__main__":
    raise SystemExit(main())
