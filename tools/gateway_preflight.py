#!/usr/bin/env python3
import argparse, hashlib, json, sys, uuid
from datetime import datetime, timezone
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--envelope',required=True)
p.add_argument('--workload-id')
p.add_argument('--required-skill')
p.add_argument('--required-target')
p.add_argument('--required-effect-ceiling')
a=p.parse_args()

def hold(reason,**extra):
    print(json.dumps({'decision':'HOLD','reason':reason,**extra},sort_keys=True)); sys.exit(1)

try:
    raw=Path(a.envelope).read_bytes(); e=json.loads(raw)
except Exception as x:
    hold('ENVELOPE_UNREADABLE',error=type(x).__name__)

req={'schema','carrier_episode_uuid','observed_utc','harness','skills','capabilities','authority','admission'}
missing=sorted(req-set(e)) if isinstance(e,dict) else sorted(req)
if missing: hold('SCHEMA_REQUIRED_FIELDS',missing=missing)
if not isinstance(e['skills'],dict): hold('SKILLS_TYPE')
if not isinstance(e['capabilities'],list): hold('CAPABILITIES_TYPE')
if not isinstance(e['authority'],dict): hold('AUTHORITY_TYPE')
if not isinstance(e['admission'],dict): hold('ADMISSION_TYPE')
if e.get('schema')!='hfo.carrier-capability-envelope.v1': hold('SCHEMA_ID')
try: uuid.UUID(e['carrier_episode_uuid'])
except Exception: hold('CARRIER_UUID')
try: datetime.fromisoformat(e['observed_utc'].replace('Z','+00:00'))
except Exception: hold('OBSERVED_UTC_INVALID')
fresh=e.get('fresh_until')
if not fresh: hold('FRESH_UNTIL_REQUIRED')
try: expiry=datetime.fromisoformat(fresh.replace('Z','+00:00')).astimezone(timezone.utc)
except Exception: hold('FRESH_UNTIL_INVALID')
if expiry<=datetime.now(timezone.utc): hold('ENVELOPE_STALE',fresh_until=fresh)

adm=e['admission']
if adm.get('decision')!='ADMIT': hold('WORKLOAD_NOT_ADMITTED',declared=adm.get('decision'))
if not adm.get('workload_id'): hold('WORKLOAD_ID_REQUIRED')
if a.workload_id and adm.get('workload_id')!=a.workload_id:
    hold('WORKLOAD_ID_MISMATCH',expected=a.workload_id,declared=adm.get('workload_id'))

skill=a.required_skill or adm.get('required_skill')
if skill:
    s=e['skills']
    if s.get('validation')!='PASS': hold('SKILL_VALIDATION',declared=s.get('validation'))
    if skill not in s.get('discovered',[]): hold('SKILL_NOT_DISCOVERED',skill=skill)
    if skill not in s.get('loaded',[]): hold('SKILL_NOT_LOADED',skill=skill)
target=a.required_target or adm.get('required_target')
if target:
    caps=[c for c in e['capabilities'] if c.get('id')==target]
    if len(caps)!=1: hold('TARGET_NOT_UNIQUE',target=target,count=len(caps))
    c=caps[0]
    if c.get('reachable')!='PROVEN': hold('TARGET_NOT_PROVEN',target=target)
    if c.get('admission')!='ADMITTED': hold('TARGET_NOT_ADMITTED',target=target)
    if not c.get('target_binding'): hold('TARGET_BINDING_REQUIRED',target=target)
    if not c.get('evidence_ref'): hold('TARGET_EVIDENCE_REQUIRED',target=target)

auth=e['authority']; effect=auth.get('effect_ceiling')
if not effect: hold('EFFECT_CEILING_REQUIRED')
if a.required_effect_ceiling and effect!=a.required_effect_ceiling:
    hold('EFFECT_CEILING_MISMATCH',expected=a.required_effect_ceiling,declared=effect)
if not auth.get('authority_ref'): hold('AUTHORITY_REF_REQUIRED')

out={'decision':'ADMIT','carrier_episode_uuid':e['carrier_episode_uuid'],
     'workload_id':adm['workload_id'],'skill':skill,'target':target,
     'effect_ceiling':effect,'fresh_until':fresh,
     'envelope_sha256':hashlib.sha256(raw).hexdigest()}
print(json.dumps(out,sort_keys=True))
