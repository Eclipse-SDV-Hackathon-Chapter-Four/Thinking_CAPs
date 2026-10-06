#!/usr/bin/env python3
"""Attach QEMU's framed Ethernet socket to a TAP in an openDuT peer namespace."""
import argparse
import fcntl
import json
import os
import select
import signal
import socket
import struct
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--listen', required=True)
    p.add_argument('--port', type=int, default=19092)
    p.add_argument('--interface', default='sdvvm0')
    a = p.parse_args()
    tap = os.open('/dev/net/tun', os.O_RDWR | os.O_NONBLOCK)
    # IFF_TAP | IFF_NO_PI, nonpersistent: descriptor close removes only this TAP.
    fcntl.ioctl(tap, 0x400454CA, struct.pack('16sH', a.interface.encode(), 0x1002))
    subprocess.run(['ip', 'link', 'set', a.interface, 'master', 'br-opendut'], check=True)
    subprocess.run(['ip', 'link', 'set', a.interface, 'up'], check=True)
    counters = {'qemu_to_tap': 0, 'tap_to_qemu': 0}
    running = True
    def stop(_s, _f):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        with socket.socket() as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((a.listen, a.port))
            server.listen(1)
            server.settimeout(.5)
            print(json.dumps({'event': 'ready', 'interface': a.interface, 'bridge': 'br-opendut'}), flush=True)
            while running:
                try:
                    stream, _ = server.accept()
                except socket.timeout:
                    continue
                with stream:
                    buffer = b''
                    while running:
                        ready, _, _ = select.select([tap, stream], [], [], .5)
                        if tap in ready:
                            frame = os.read(tap, 65536)
                            stream.sendall(struct.pack('!I', len(frame)) + frame)
                            counters['tap_to_qemu'] += 1
                        if stream in ready:
                            chunk = stream.recv(65536)
                            if not chunk:
                                break
                            buffer += chunk
                            while len(buffer) >= 4:
                                length = struct.unpack('!I', buffer[:4])[0]
                                if not 14 <= length <= 65535:
                                    raise RuntimeError('Invalid QEMU Ethernet frame size')
                                if len(buffer) < 4 + length:
                                    break
                                os.write(tap, buffer[4:4 + length])
                                buffer = buffer[4 + length:]
                                counters['qemu_to_tap'] += 1
    finally:
        os.close(tap)
        print(json.dumps({'event': 'stopped', **counters, 'tap_removed': True}), flush=True)


if __name__ == '__main__':
    main()
