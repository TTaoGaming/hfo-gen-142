"""Read-only reduction of existing pilot receipts; no collector or scheduler."""
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def seconds(start, end):
    if not start or not end:
        return None
    delta = (datetime.fromisoformat(end.replace('Z', '+00:00')) -
             datetime.fromisoformat(start.replace('Z', '+00:00'))).total_seconds()
    if delta < 0:
        raise ValueError('REVERSED_TIMESTAMPS')
    return round(delta, 6)


def reduce_receipt(data):
    rows = data.get('provider_rows', [])
    metrics = data.get('native_metrics', {})
    evaluated = [name for name, value in metrics.items()
                 if re.fullmatch(r'results/gen_[1-9][0-9]*/results/metrics.json', name)
                 and value.get('public', {}).get('reason') == 'COMPLETE'
                 and value.get('public', {}).get('trial_count', 0) > 0]
    return {
        'work_id': data.get('work_id'),
        'campaign_wall_seconds': seconds(data.get('service_started_utc'), data.get('service_finished_utc')),
        'dispatched_requests': sum(row.get('dispatched') is True for row in rows),
        'returned_responses': sum(row.get('state') == 'RETURNED' for row in rows),
        'native_evaluated_proposals': len(evaluated),
        'native_evaluation_receipts': evaluated,
        'baseline_and_separate_replays_excluded': True,
        'request_slots': [dict(provider=row.get('provider'), model=row.get('model'),
            state=row.get('state'),
            reserved_to_returned_seconds=seconds(row.get('reserved_utc'), row.get('finished_utc')))
            for row in rows],
        'evaluation_seconds': {name: value.get('private', {}).get('elapsed_seconds')
                               for name, value in metrics.items()},
        'independent_accepted_candidate_count': None,
        'end_to_end_candidate_cycle_seconds': None,
        'measured_takt_seconds': None,
        'operator_interventions': None,
        'verified_new_champions': 0 if data.get('winner_found') is False else None,
        'time_to_winner_seconds': None,
        'claim_ceiling': 'Historical receipt reduction, not live telemetry. Missing acceptance/phase timestamps remain unknown. Call-slot time includes admission overhead. Campaign duration is not candidate cycle time; takt is a demand target, not a measured latency.'
    }


if __name__ == '__main__':
    path = Path(sys.argv[1])
    raw = path.read_bytes()
    result = reduce_receipt(json.loads(raw))
    result['source_sha256'] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(result, indent=2))
