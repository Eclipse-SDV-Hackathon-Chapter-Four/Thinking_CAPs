"""Connection-boundary regressions; actual simulator evidence is separate."""
import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from owned_carla import correlate_return_actuation, wait_for_world


class ReadinessTests(unittest.TestCase):
    def test_failed_client_is_replaced_before_retry(self):
        failed, ready = Mock(), Mock()
        failed.get_world.side_effect = RuntimeError('connection failed before bind')
        world = object()
        ready.get_world.return_value = world
        factory = Mock(side_effect=[failed, ready])
        attempts = []
        with patch('owned_carla.time.sleep'):
            result = wait_for_world(factory, lambda: True, 5, attempts.append)
        self.assertEqual(result, (world, ready))
        self.assertEqual(factory.call_count, 2)
        failed.get_world.assert_called_once()
        self.assertEqual(len(attempts), 1)

    def test_expired_deadline_does_not_create_another_client(self):
        failed = Mock()
        failed.get_world.side_effect = RuntimeError('not ready')
        factory = Mock(return_value=failed)
        with patch('owned_carla.time.monotonic', side_effect=[0, .5, 2, 2]), patch('owned_carla.time.sleep'):
            with self.assertRaisesRegex(RuntimeError, 'readiness timeout'):
                wait_for_world(factory, lambda: True, 1, lambda _: None)
        factory.assert_called_once()
        failed.set_timeout.assert_called_once_with(.5)

    def test_exited_server_is_not_treated_as_retryable_readiness(self):
        factory = Mock()
        with self.assertRaisesRegex(RuntimeError, 'exited before readiness'):
            wait_for_world(factory, lambda: False, 5, lambda _: None)
        factory.assert_not_called()


class ActuationTests(unittest.TestCase):
    def sample(self, **changes):
        return dict({'frame': 1, 'observed_at_monotonic_ns': 10, 'cc_engaged': True,
                     'operator_acc_pedal': 0, 'score_throttle_received_by_vcu': .6,
                     'vcu_throttle_command': .5, 'applied_throttle': .5}, **changes)

    def test_positive_pedal_or_unrelated_actuation_cannot_prove_native_return(self):
        for first in (self.sample(operator_acc_pedal=.7), self.sample(cc_engaged=False),
                      self.sample(vcu_throttle_command=.4)):
            self.assertEqual(correlate_return_actuation([first, self.sample(frame=2)], 1.2, (0, 1))['match_count'], 0)
        self.assertEqual(correlate_return_actuation([self.sample(), self.sample(frame=2, applied_throttle=.4)], 1.2, (0, 1))['match_count'], 0)

    def test_normalized_native_request_requires_subsequent_physical_match(self):
        evidence = correlate_return_actuation([self.sample(), self.sample(frame=2, observed_at_monotonic_ns=20)], 1.2, (0, 1))
        self.assertEqual(evidence['match_count'], 1)
        self.assertEqual(evidence['matches'][0]['applied_frame'], 2)
        self.assertEqual(evidence['matches'][0]['observation_delta_ns'], 10)
