"""Offline shape checks only. Requires jsonschema; no runtime admission."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

p = Path(__file__).resolve().parent
schema = json.loads((p / 'hatchery.schema.json').read_text())
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, format_checker=FormatChecker())
examples = json.loads((p / 'examples.json').read_text())
for example in examples:
    validator.validate(example)

mutations = {
    'unknown ABI': lambda d: d.update(abi='gen142.hatchery/99'),
    'missing owner': lambda d: d.pop('owners'),
    'missing budget': lambda d: d['limits'].pop('max_usd'),
    'unbounded time': lambda d: d['limits'].update(lifetime_seconds=None),
    'negative disk': lambda d: d['limits'].update(workspace_bytes=-1),
    'scale before G3': lambda d: d['limits'].update(active_attempts=2),
    'credential field': lambda d: d.update(api_key='synthetic-not-a-secret'),
    'unknown adapter': lambda d: d['adapters'][0].update(kind='magic'),
    'invalid UTC': lambda d: d.update(observed_utc='yesterday'),
}
for name, mutate in mutations.items():
    candidate = copy.deepcopy(examples[0])
    mutate(candidate)
    assert list(validator.iter_errors(candidate)), name
print(f'{len(examples)} platform fixtures accepted; {len(mutations)} hostile shapes rejected; runtime UNPROVEN')
