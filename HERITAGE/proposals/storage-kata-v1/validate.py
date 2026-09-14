"""Validate the bounded public event proposals; no network, writes or deletion."""
import json, pathlib, re, sys
from jsonschema import Draft202012Validator, FormatChecker
base=pathlib.Path(__file__).resolve().parent
schema=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else base.parents[2]/'schemas/strife-splendor-event-v1.schema.json'
validator=Draft202012Validator(json.loads(schema.read_text()),format_checker=FormatChecker())
seen=set()
def require(condition):
    if not condition:
        raise ValueError('Proposal contract check failed')
for name in ('strife.json','splendor.json'):
    event=json.loads((base/name).read_text())
    validator.validate(event)
    require(event['data']['classification']==pathlib.Path(name).stem.upper())
    key=(event['source'],event['id']);require(key not in seen);seen.add(key)
    require(event['type']==f"dev.worldweaver.{event['data']['classification'].lower()}.v1")
    require(event['data']['status']=='SOURCED' and event['data']['consumer_refs']==[])
    require('traceparent' not in event and 'tracestate' not in event)
    for evidence in event['data']['evidence']:
        require(re.fullmatch('[0-9a-f]{64}',evidence['content_sha256']))
        require(evidence['visibility']=='PRIVATE' and evidence['ref'] is None)
    raw=json.dumps(event)
    require(not any(x in raw for x in ('C:\\','drive.google.com','AppData','access_token','refresh_token')))
    require(re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}',raw) is None)
print('PASS: 2 schema-valid SOURCED events; pairing, privacy fields, hash width, no invented trace or ConsumerAck')
