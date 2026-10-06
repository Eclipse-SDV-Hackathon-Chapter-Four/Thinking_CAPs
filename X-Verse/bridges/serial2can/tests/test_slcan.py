"""Unit tests of the SLCAN codec and the bridge's ID filter and echo guard."""
import sys
import time
from pathlib import Path

import can
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import slcan
from serial2can_bridge import EchoGuard, IdFilter


def message(ident, data=b"", extended=False, remote=False, dlc=None):
    return can.Message(arbitration_id=ident, data=data, is_extended_id=extended, is_remote_frame=remote,
                       dlc=len(data) if dlc is None else dlc)


@pytest.mark.parametrize("status", range(256))
def test_status_byte_round_trip(status):
    original = message(0x1F1, bytes([status, 0xA5, 0, 0, 0, 0, 0, 0xFF]))
    line = slcan.encode(original)
    assert line.endswith(b"\r") and len(line) == 22
    decoded = slcan.decode(line[:-1])
    assert decoded.equals(original, timestamp_delta=None)


@pytest.mark.parametrize("msg, line", [
    (message(0x1F4, bytes([3]) + bytes(7)), b"t1F480300000000000000\r"),
    (message(0x7FF), b"t7FF0\r"),
    (message(0x1ABCDEF0, bytes([1, 2, 3, 4, 5, 6, 7, 0xFF]), extended=True), b"T1ABCDEF0801020304050607FF\r"),
    (message(0x123, remote=True, dlc=4), b"r1234\r"),
    (message(0x1F1, remote=True, extended=True, dlc=2), b"R000001F12\r"),
])
def test_encode_exact(msg, line):
    assert slcan.encode(msg) == line
    assert slcan.decode(line[:-1]).equals(msg, timestamp_delta=None)


def test_decode_accepts_lowercase_and_timestamp():
    decoded = slcan.decode(b"t1f480300000000000000ABCD")
    assert decoded.arbitration_id == 0x1F4 and decoded.data[0] == 3


@pytest.mark.parametrize("line", [
    b"", b"x", b"t1F1", b"t1F18", b"t1F1806", b"t1F18060000000000000", b"t1F1806000000000000000",
    b"t8000", b"t1F19", b"t1F1G", b"tXYZ0", b"T200000000", b"T1F1806", b"r1F1800", b"z",
])
def test_decode_rejects_malformed(line):
    with pytest.raises(slcan.SlcanError):
        slcan.decode(line)


@pytest.mark.parametrize("msg", [
    message(0x800), message(0x20000000, extended=True),
    can.Message(arbitration_id=0x1F1, is_error_frame=True),
    can.Message(arbitration_id=0x1F1, is_fd=True, data=bytes(12)),
])
def test_encode_rejects_unsupported(msg):
    with pytest.raises(slcan.SlcanError):
        slcan.encode(msg)


def test_splitter_tokens_across_chunks():
    splitter = slcan.LineSplitter()
    first = list(splitter.feed(b"\rz\rt1F48030000"))
    rest = list(splitter.feed(b"0000000000\r\x07V1010\r\n"))
    assert first == [b"", b"z"]
    assert rest == [b"t1F480300000000000000", slcan.BELL, b"V1010"]


def test_splitter_flags_overlong_lines():
    assert slcan.tokens(b"t" + b"0" * 60 + b"\rz\r") == [None, b"z"]


def test_id_filter():
    exact = IdFilter([{"id": "0x1F1"}])
    assert exact.matches(message(0x1F1)) and not exact.matches(message(0x1F2))
    pair = IdFilter([{"id": "0x1F4", "mask": "0x7FE", "extended": False}])
    assert pair.matches(message(0x1F4)) and pair.matches(message(0x1F5))
    assert not pair.matches(message(0x1F6)) and not pair.matches(message(0x1F4, extended=True))
    assert IdFilter(None).matches(message(0x123)) and IdFilter([]).matches(message(0x1ABCDEF, extended=True))


def test_echo_guard_cancels_one_echo_per_send():
    guard = EchoGuard(0.2)
    frame = message(0x1F4, bytes(8))
    guard.sent(frame)
    assert guard.is_echo(frame) and not guard.is_echo(frame)
    guard.sent(frame)
    time.sleep(0.25)
    assert not guard.is_echo(frame)
    assert not guard.is_echo(message(0x1F4, bytes([1]) + bytes(7)))
