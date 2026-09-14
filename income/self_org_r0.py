#!/usr/bin/env python3
import json, os, re, sys, uuid, urllib.request
from datetime import datetime, timezone

REPO = os.getenv("HFO_REPO", "TTaoGaming/hfo-gen-142")
ISSUE = int(os.getenv("HFO_ISSUE", "7"))
MODEL = os.getenv("HFO_OLLAMA_MODEL", "granite4.2:3b-q4_K_M")
NEURAL_TIMEOUT = float(os.getenv("HFO_NEURAL_TIMEOUT", "8"))
CAPS = {x.strip() for x in os.getenv("HFO_CAPABILITIES", "public_web,github_read,local_shell,ollama").split(",") if x.strip()}
API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
UA = {"User-Agent": "gen142-income-selforg-r0"}

def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15) as r: return json.load(r)

def post_json(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=NEURAL_TIMEOUT) as r: return json.load(r)

def extract_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m: return {}
    try: return json.loads(m.group(0))
    except Exception: return {}

def main():
    config = get_json(f"{RAW}/{REPO}/main/income/self_org_r0.json")
    comments = get_json(f"{API}/repos/{REPO}/issues/{ISSUE}/comments?per_page=100")
    bodies = [c.get("body", "") for c in comments]
    occupancy = {k: 0 for k in config["lanes"]}
    for body in bodies:
        for lane in re.findall(r"(?im)^\s*(?:selected_lane|lane)\s*:\s*(I[0-9])\b", body):
            if lane in occupancy: occupancy[lane] += 1
    terminal_count = sum(bool(re.search(r"(?i)\bterminal\b|state_after\s*:\s*(?:PASS|HOLD|KILL|WEAKEN)", b)) for b in bodies)

    max_claims = {"LING":4, "TWINLING":4, "ROACH":3, "REDUCER":4}
    eligible, capability_holds = [], {}
    for lane, spec in config["lanes"].items():
        required = set(spec.get("required_capabilities", []))
        missing = sorted(required - CAPS)
        if missing:
            capability_holds[lane] = missing; continue
        need = int(spec.get("requires_terminals", 0))
        cap = max_claims.get(spec.get("phenotype"), 3)
        if terminal_count < need or occupancy[lane] >= cap: continue
        score = int(spec["priority"]) - 18 * occupancy[lane]
        eligible.append({"lane":lane,"score":score,"occupancy":occupancy[lane],**spec})
    if not eligible:
        print(json.dumps({"decision":"HOLD","reason":"NO_ELIGIBLE_LANE","capabilities":sorted(CAPS),"capability_holds":capability_holds,"occupancy":occupancy,"terminals":terminal_count},indent=2)); return 2
    eligible.sort(key=lambda x: (-x["score"], x["lane"]))
    symbolic_top = eligible[0]["score"]
    neural_pool = [x for x in eligible if x["score"] >= symbolic_top - 5]
    neural = {}
    try:
        prompt = "Choose ONE lane from this already-symbolically-eligible set. Optimize for fastest credible external income signal. Do not invent authority. Return JSON only: {selected_lane,rationale}.\n" + json.dumps(neural_pool)
        resp = post_json("http://127.0.0.1:11434/api/chat", {"model":MODEL,"stream":False,"messages":[{"role":"user","content":prompt}],"options":{"temperature":0,"num_predict":64}})
        neural = extract_json(resp.get("message",{}).get("content",""))
    except Exception as e: neural = {"error": type(e).__name__}
    candidate = next((x for x in neural_pool if x["lane"] == neural.get("selected_lane")), eligible[0])
    episode = str(uuid.uuid4()); now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    durable_write = "github_write" in CAPS
    out = {"schema":"hfo.gen142.income-claim.v1","carrier_episode_uuid":episode,"utc":now,"control_issue":ISSUE,
      "selected_lane":candidate["lane"],"phenotype":candidate["phenotype"],"mission":candidate["mission"],
      "symbolic_score":candidate["score"],"occupancy_before":candidate["occupancy"],"terminal_count_observed":terminal_count,
      "capabilities":sorted(CAPS),"capability_holds":capability_holds,"neural_advisory":neural,
      "claim_state":"READY_TO_CLAIM" if durable_write else "PROPOSED_LOCAL__NEEDS_DURABLE_WRITER",
      "effect_ceiling":config["effect_ceiling"],"tao_relay_required":False}
    os.makedirs("receipts",exist_ok=True)
    with open(f"receipts/{episode}.json","w") as f: json.dump(out,f,indent=2,sort_keys=True)
    print(json.dumps(out,indent=2,sort_keys=True)); return 0

if __name__ == "__main__": sys.exit(main())
