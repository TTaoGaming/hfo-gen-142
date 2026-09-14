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
        'README.md','AGENTS.md','GATEWAY.md','GENE_SEED.md','KNOWLEDGE_PROTOCOL.md',
        'WORLD_STATE/latest.md','BATON_PASS.md','RECOVERY_SWARM.md','WORK_QUEUE.md',
        'HIVE_GATEWAY.md','WAVE2_STRIFE_SPLENDOR.md','BURROW.md','CELL0_HANDOFF.md',
        '.agents/skills/roach-fanin/SKILL.md',
        'HANDOFF/2026-09-14-baton.md','HANDOFF/2026-09-14-zerg-swarm-thread-handoff.md',
    ]
    stale = re.compile(r'(recover(?: issue)? #(1|2|3|6)(?!\d)|issue #(1|2|3|6) newest-first)', re.I)
    for rel in surfaces:
        text = (ROOT / rel).read_text(encoding='utf-8')
        assert '#13' in text, rel
        assert not stale.search(text), rel
    kp = (ROOT / 'KNOWLEDGE_PROTOCOL.md').read_text(encoding='utf-8')
    assert 'WORLD_STATE/index.json' not in kp
    assert 'WORLD_STATE/partials' not in kp
