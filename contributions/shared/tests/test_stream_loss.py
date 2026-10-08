"""Stream-loss assertions must tolerate a moving plant without hiding a bypass."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[3] / 'contributions/eclipse-opendut/OpenDut/tests/opendut_receiver_smoke.py'
spec = importlib.util.spec_from_file_location('stream_loss', MODULE)
stream_loss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stream_loss)


class StreamLossTests(unittest.TestCase):
    def view(self, accepted=990, freshness='stale', receiver='available', speed=48.395809):
        return {'receiver_state': receiver, 'freshness_state': freshness,
                'observation': {'last_accepted_at_monotonic_ns': accepted, 'vehicle_speed': speed}}

    def test_moving_sample_accepted_before_cut_is_valid(self):
        self.assertTrue(stream_loss.stream_stopped_after_cut(self.view(), 1000, 100))

    def test_bounded_inflight_delivery_is_valid(self):
        self.assertTrue(stream_loss.stream_stopped_after_cut(self.view(1100), 1000, 100))

    def test_continuing_acceptance_fails_even_at_constant_speed(self):
        self.assertFalse(stream_loss.stream_stopped_after_cut(self.view(1101, speed=42.5), 1000, 100))

    def test_fresh_receiver_cannot_pass(self):
        self.assertFalse(stream_loss.stream_stopped_after_cut(self.view(freshness='fresh'), 1000, 100))

    def test_missing_or_unavailable_observation_cannot_pass(self):
        for value in (self.view(receiver='unknown'), self.view(accepted=None), self.view(accepted=True), {}):
            with self.subTest(value=value):
                self.assertFalse(stream_loss.stream_stopped_after_cut(value, 1000, 100))
