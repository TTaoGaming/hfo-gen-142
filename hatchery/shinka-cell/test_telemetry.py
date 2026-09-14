import unittest
from telemetry import reduce_receipt, seconds


class TelemetryTests(unittest.TestCase):
    def test_missing_is_not_zero_or_success(self):
        result = reduce_receipt({})
        self.assertIsNone(result['campaign_wall_seconds'])
        self.assertIsNone(result['verified_new_champions'])
        self.assertIsNone(result['operator_interventions'])

    def test_baseline_and_offline_replay_do_not_become_native_generations(self):
        complete = {'public': {'reason': 'COMPLETE', 'trial_count': 8}}
        result = reduce_receipt({'native_metrics': {
            'results/gen_0/results/metrics.json': complete,
            'replay-kimi/metrics.json': complete,
            'results/gen_2/results/metrics.json': complete,
            'results/gen_3/results/metrics.json': {'public': {'reason': 'FAILED'}}}})
        self.assertEqual(result['native_evaluated_proposals'], 1)
        self.assertIsNone(result['independent_accepted_candidate_count'])

    def test_reversed_timestamps_fail(self):
        with self.assertRaises(ValueError):
            seconds('2026-09-14T01:00:01Z', '2026-09-14T01:00:00Z')


if __name__ == '__main__':
    unittest.main()
