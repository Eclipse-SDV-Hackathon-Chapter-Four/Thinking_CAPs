"""Lawicell SLCAN line codec for classic CAN (CAN 2.0A/B, DLC 0..8).

Host -> device and device -> host frames share one ASCII format:

    tIIIL<data>     standard data frame      TIIIIIIIIL<data>  extended data frame
    rIIIL           standard remote frame    RIIIIIIIIL        extended remote frame

each terminated by CR. A device may append a 4-hex-digit timestamp (``Z1``),
which is accepted and ignored. Devices answer commands with CR (ok), BELL
(error), ``z``/``Z`` (frame accepted) or a response such as ``V1010``.
"""
import re

import can

CR, BELL = b"\r", b"\x07"
CAN_MAX_DLEN = 8
SFF_MASK, EFF_MASK = 0x7FF, 0x1FFFFFFF
TIMESTAMP_DIGITS = 4
MAX_LINE = 1 + 8 + 1 + 2 * CAN_MAX_DLEN + TIMESTAMP_DIGITS  # longest frame line
_HEX = re.compile(rb"^[0-9A-Fa-f]*$")
# Frame line letter <-> (extended identifier, remote frame).
_KINDS = {b"t": (False, False), b"T": (True, False), b"r": (False, True), b"R": (True, True)}
_LETTERS = {flags: letter.decode() for letter, flags in _KINDS.items()}


class SlcanError(ValueError):
    """A frame line that does not follow the SLCAN syntax."""


def _check_encodable(message: can.Message) -> None:
    if message.is_error_frame or message.is_fd:
        raise SlcanError("error and CAN FD frames cannot be carried by SLCAN")
    if not 0 <= message.dlc <= CAN_MAX_DLEN:
        raise SlcanError(f"DLC {message.dlc} out of range")
    if not 0 <= message.arbitration_id <= (EFF_MASK if message.is_extended_id else SFF_MASK):
        raise SlcanError(f"identifier {message.arbitration_id:#x} out of range")
    if not message.is_remote_frame and len(message.data) < message.dlc:
        raise SlcanError("data shorter than DLC")


def encode(message: can.Message) -> bytes:
    """SLCAN line (with CR) for a classic CAN message; raises SlcanError."""
    _check_encodable(message)
    extended, remote, dlc = message.is_extended_id, message.is_remote_frame, message.dlc
    ident = f"{message.arbitration_id:08X}" if extended else f"{message.arbitration_id:03X}"
    payload = "" if remote else bytes(message.data[:dlc]).hex().upper()
    return f"{_LETTERS[(extended, remote)]}{ident}{dlc}{payload}".encode() + CR


def decode(line: bytes) -> can.Message:
    """CAN message for one frame line (without terminator); raises SlcanError."""
    kind = _KINDS.get(line[:1])
    if kind is None:
        raise SlcanError(f"not a frame line: {line!r}")
    extended, remote = kind
    id_digits = 8 if extended else 3
    header = 1 + id_digits + 1
    if len(line) < header or not _HEX.match(line[1:]):
        raise SlcanError(f"malformed frame line: {line!r}")
    ident = int(line[1:1 + id_digits], 16)
    dlc = int(line[1 + id_digits:header], 16)
    if dlc > CAN_MAX_DLEN or ident > (EFF_MASK if extended else SFF_MASK):
        raise SlcanError(f"identifier or DLC out of range: {line!r}")
    body = 0 if remote else dlc * 2
    if len(line) not in (header + body, header + body + TIMESTAMP_DIGITS):  # optional timestamp
        raise SlcanError(f"length does not match DLC: {line!r}")
    data = b"" if remote else bytes.fromhex(line[header:header + body].decode())
    return can.Message(arbitration_id=ident, is_extended_id=extended, is_remote_frame=remote,
                       dlc=dlc, data=data)


class LineSplitter:
    """Splits a device byte stream into SLCAN tokens.

    Yields each CR-terminated line without its CR (``b""`` is a bare OK) and
    each BELL as ``BELL``. LF is ignored. Lines longer than ``MAX_LINE`` are
    discarded up to the next terminator and reported once as ``None``.
    """

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._overlong = False

    def feed(self, data: bytes) -> list[bytes | None]:
        """All tokens completed by ``data``, in order; partial lines are kept."""
        out: list[bytes | None] = []
        for value in data:
            byte = bytes((value,))
            if byte == b"\n":
                continue
            if byte in (CR, BELL):
                if byte == CR or self._buffer or self._overlong:
                    out.append(None if self._overlong else bytes(self._buffer))
                self._buffer.clear()
                self._overlong = False
                if byte == BELL:
                    out.append(BELL)
            elif len(self._buffer) < MAX_LINE:
                self._buffer += byte
            else:
                self._overlong = True
        return out


def tokens(data: bytes) -> list[bytes | None]:
    """Convenience wrapper: all tokens of a complete byte string."""
    return LineSplitter().feed(data)
