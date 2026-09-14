import json, subprocess, sys, tempfile, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / 'tools' / 'gateway_preflight.py'

def env(decision='ADMIT', binding='device:oracle'):
    return {
      'schema':'hfo.carrier-capability-envelope.v1',
      'carrier_episode_uuid':str(uuid.uuid4()),
      'observed_utc':'2026-09-14T11:00:00Z','fresh_until':'2099-01-01T00:00:00Z',
      'harness':{'product':'test','model':'test','execution_surface':'test'},
      'skills':{'discovered':['twinling-pdsa'],'loaded':['twinling-pdsa'],'validation':'PASS'},
      'capabilities':[{'id':'oracle-vps','reachable':'PROVEN','admission':'ADMITTED','target_binding':binding,'evidence_ref':'test:oracle'}],
      'authority':{'effect_ceiling':'NO_EXTERNAL_EFFECT','protected_effects':[],'authority_ref':'test:authority'},
      'admission':{'workload_id':'W1','decision':decision,'reasons':[],'required_skill':'twinling-pdsa','required_target':'oracle-vps'},
      'limitations':[]}

def run(obj):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(obj,f); name=f.name
    return subprocess.run([sys.executable,str(GATE),'--envelope',name,'--workload-id','W1'],capture_output=True,text=True)

def test_valid_envelope_admits():
    r=run(env())
    assert r.returncode==0, r.stdout+r.stderr
    assert json.loads(r.stdout)['decision']=='ADMIT'

def test_hold_decision_fails_closed():
    r=run(env(decision='HOLD'))
    assert r.returncode!=0
    assert json.loads(r.stdout)['decision']=='HOLD'

def test_missing_target_binding_fails_closed():
    r=run(env(binding=None))
    assert r.returncode!=0
    assert json.loads(r.stdout)['reason']=='TARGET_BINDING_REQUIRED'

def test_unloaded_required_skill_fails_closed():
    x=env(); x['skills']['loaded']=[]
    r=run(x)
    assert r.returncode!=0
    assert json.loads(r.stdout)['reason']=='SKILL_NOT_LOADED'

def test_recovery_topology_has_one_current_trunk():
    import re
    surfaces = [
        'README.md','AGENTS.md','GATEWAY.md','GENE_SEED.md','WORLD_STATE/latest.md',
        '.agents/skills/twinling-pdsa/SKILL.md','.agents/skills/roach-fanin/SKILL.md',
    ]
    stale=re.compile(r'(recover(?: issue)? #(1|2|3|6|7|9)(?!\d)|issue #(1|2|3|6|7|9) newest-first)',re.I)
    for rel in surfaces:
        text=(ROOT/rel).read_text(encoding='utf-8')
        assert '#13' in text, rel
        assert not stale.search(text), rel

def test_retired_surfaces_are_absent_from_live_tree():
    retired = [
        'BATON_PASS.md','CELL0_HANDOFF.md','HIVE_GATEWAY.md','HIVE_R0.md','HIVE_WAVE1.md',
        'MOBILE_HQ_BRIDGE.md','RECOVERY_SWARM.md','WAVE2_STRIFE_SPLENDOR.md','WORK_QUEUE.md',
        'WORLD_STATE/HQ_LOOP_R1.md','BRIDGES/CHATGPT_CLOUD_INPUT.md','income/BATON_SELF_ORG_R1.md',
        'income/self_org_r0.py','income/self_org_r0.json','cell0/src/index.js','cell0/wrangler.jsonc',
        'KNOWLEDGE_PROTOCOL.md',
        'schemas/holon-mission-v1.schema.json','schemas/knowledge-event-v0.json',
        'schemas/oracle-hq-canary-v1.schema.json','schemas/world-state-capsule-v0.json',
        'experiments/harbor/H3_PUBLIC_PROOF_SUBMISSION.md','experiments/packing/H3_PACKOMANIA_PUBLIC_PROOF.md',
        'tools/crown_gate.py','tests/test_crown_gate.py','.github/workflows/oracle-cell-r0.yml',
    ]
    assert not (ROOT/'HANDOFF').exists()
    for rel in retired: assert not (ROOT/rel).exists(), rel

def test_mutable_status_not_cached_in_oracle_design_profiles():
    # ORACLE_HQ is collision-protected by the newer deterministic reconciler path.
    # ORACLE_GATEWAY remains a stable design profile and must not cache mutable blockers.
    oracle=(ROOT/'ORACLE_GATEWAY.md').read_text(encoding='utf-8')
    assert 'NOT CURRENT RUNTIME TRUTH' in oracle
    assert '#13' in oracle and '#8' in oracle
    assert '## Current exact blockers' not in oracle
    gateway=(ROOT/'GATEWAY.md').read_text(encoding='utf-8')
    assert 'Load `ORACLE_HQ.md` / `ORACLE_GATEWAY.md` only when Oracle placement is actually being considered.' in gateway
