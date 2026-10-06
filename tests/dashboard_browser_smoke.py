#!/usr/bin/env python3
"""Actual Chromium checks; fixture/historical UI checks do not establish vehicle success."""
import argparse
import base64
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import struct
import subprocess
import tempfile
import time
import urllib.request


class Browser:
    def __init__(self, executable, url, output):
        self.profile = tempfile.TemporaryDirectory(prefix='sdv-dashboard-browser-')
        self.log = Path(output).open('wb')
        self.process = subprocess.Popen([executable, '--headless', '--no-sandbox', '--disable-gpu',
            '--no-first-run', '--no-default-browser-check', '--remote-debugging-port=0',
            '--remote-allow-origins=http://localhost', '--user-data-dir=' + self.profile.name, url],
            stdout=self.log, stderr=subprocess.STDOUT, start_new_session=True)
        self.channel = None
        self.number = 0
        self.errors = []
        try:
            deadline = time.monotonic() + 15
            portfile = Path(self.profile.name) / 'DevToolsActivePort'
            while not portfile.exists():
                if time.monotonic() > deadline: raise RuntimeError('Browser readiness timeout')
                time.sleep(.05)
            port = int(portfile.read_text().splitlines()[0])
            targets = json.load(urllib.request.urlopen('http://127.0.0.1:' + str(port) + '/json/list'))
            url = next(t['webSocketDebuggerUrl'] for t in targets if t['type'] == 'page')
            path = url.split(str(port), 1)[1]
            self.channel = socket.create_connection(('127.0.0.1', port), timeout=5)
            self.channel.settimeout(8)
            key = base64.b64encode(secrets.token_bytes(16)).decode()
            self.channel.sendall(('GET ' + path + ' HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: ' + key + '\r\nSec-WebSocket-Version: 13\r\nOrigin: http://localhost\r\n\r\n').encode())
            header = b''
            while not header.endswith(b'\r\n\r\n'): header += self.channel.recv(1)
            if not header.startswith(b'HTTP/1.1 101'): raise RuntimeError('Debugger handshake rejected')
            self.call('Runtime.enable'); self.call('Page.enable')
            self.call('Emulation.setFocusEmulationEnabled', {'enabled': True})
        except Exception:
            self.close()
            raise

    def exact(self, size):
        data = b''
        while len(data) < size:
            chunk = self.channel.recv(size - len(data))
            if not chunk: raise RuntimeError('Debugger closed')
            data += chunk
        return data

    def call(self, method, params=None):
        self.number += 1
        payload = json.dumps({'id': self.number, 'method': method, 'params': params or {}}).encode()
        mask = secrets.token_bytes(4); size = len(payload)
        header = bytes([0x81,0x80|size]) if size < 126 else bytes([0x81,0xfe])+struct.pack('!H',size) if size<65536 else bytes([0x81,0xff])+struct.pack('!Q',size)
        self.channel.sendall(header + mask + bytes(v ^ mask[i % 4] for i, v in enumerate(payload)))
        while True:
            first, second = self.exact(2); size = second & 127
            if size == 126: size = struct.unpack('!H', self.exact(2))[0]
            elif size == 127: size = struct.unpack('!Q', self.exact(8))[0]
            value = json.loads(self.exact(size))
            if value.get('method') == 'Runtime.exceptionThrown': self.errors.append(value)
            if value.get('id') == self.number:
                if 'error' in value: raise RuntimeError(str(value['error']))
                return value['result']

    def evaluate(self, expression):
        value = self.call('Runtime.evaluate', {'expression': expression, 'returnByValue': True, 'awaitPromise': True})
        if 'exceptionDetails' in value: raise RuntimeError(str(value['exceptionDetails']))
        return value['result'].get('value')

    def wait(self, expression, timeout=8):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.evaluate(expression): return True
            time.sleep(.1)
        return False

    def screenshot(self, path, width=1280, height=900):
        self.call('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': width<720})
        time.sleep(.1)
        Path(path).write_bytes(base64.b64decode(self.call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': True})['data']))

    def key(self, key, code):
        self.call('Input.dispatchKeyEvent', {'type':'rawKeyDown','key':key,'code':key,'windowsVirtualKeyCode':code})
        if key == 'Enter':
            self.call('Input.dispatchKeyEvent', {'type':'char','text':'\r','key':key,'code':key,'windowsVirtualKeyCode':code})
        self.call('Input.dispatchKeyEvent', {'type':'keyUp','key':key,'code':key,'windowsVirtualKeyCode':code})

    def close(self):
        if self.channel: self.channel.close()
        if self.process.poll() is None:
            os.killpg(self.process.pid, signal.SIGTERM)
            try: self.process.wait(timeout=5)
            except subprocess.TimeoutExpired: os.killpg(self.process.pid, signal.SIGKILL); self.process.wait(timeout=3)
        self.log.close(); self.profile.cleanup()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8791')
    parser.add_argument('--chrome', default='/home/jefferson/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    browser = None; checks = []
    def check(identity, value):
        checks.append({'id': identity, 'passed': bool(value)})
        if not value: raise AssertionError(identity)
    try:
        browser = Browser(args.chrome, args.url, args.output / 'browser.log')
        check('loaded-native-unavailable-truth', browser.wait('typeof snapshot!=="undefined" && snapshot!==null && $("service-status").dataset.state==="unavailable" && $("freshness").dataset.state==="unknown"'))
        browser.screenshot(args.output / 'diagnosis-desktop.png')
        check('keyboard-primary-navigation', browser.evaluate('$("nav-tests").focus();document.activeElement.id==="nav-tests"'))
        browser.call('Input.dispatchKeyEvent', {'type': 'rawKeyDown', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13})
        browser.call('Input.dispatchKeyEvent', {'type': 'char', 'text': '\r', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13})
        browser.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13})
        check('keyboard-test-view', browser.wait('!$("tests-view").hidden && $("diagnosis-view").hidden'))
        # Use native select keyboard events, including the real change handler.
        browser.evaluate('$("run-select").focus()')
        browser.key('Home', 36)
        steps=browser.evaluate('Array.from($("run-select").options).findIndex(o=>o.value==="physical")')
        for _ in range(steps): browser.key('ArrowDown', 40)
        browser.key('Enter', 13)
        check('keyboard-evidence-selection', browser.wait('selected==="physical" && $("evidence-verdict").textContent.includes("passed")'))
        check('historical-physical-selection', browser.evaluate('selected="physical";$("run-select").value=selected;epoch++;evidence().then(()=>$("evidence-mode").textContent.startsWith("Historical record")&&$("evidence-verdict").textContent.includes("passed")&&!$("replay").hidden)'))
        check('verified-downloads', browser.evaluate('document.querySelectorAll("#downloads a").length>=8 && $("integrity").textContent==="verified"'))
        browser.screenshot(args.output / 'tests-desktop.png')
        browser.screenshot(args.output / 'tests-mobile.png', 360, 900)
        check('360-width-no-page-overflow', browser.evaluate('document.documentElement.scrollWidth<=360'))
        check('mobile-verdicts-remain-horizontal', browser.evaluate('document.querySelector("table").getBoundingClientRect().width>=560 && getComputedStyle(document.querySelector("td:nth-child(2)")).whiteSpace==="nowrap"'))
        browser.evaluate('document.querySelector(".table-wrap").focus()')
        browser.key('ArrowRight', 39)
        check('mobile-table-keyboard-scroll', browser.wait('document.querySelector(".table-wrap").scrollLeft>0'))
        # Actual keyboard start with stopped bench records blocked, never a pass.
        browser.evaluate('$("campaign").focus()'); browser.key('Home',36)
        browser.evaluate('$("start").focus()'); browser.key('Enter',13)
        check('mobile-keyboard-blocked-campaign', browser.wait('$("evidence-verdict").textContent.includes("blocked")',10))
        check('completed-cleanup-separate-from-verdict', browser.evaluate('$("evidence-info").textContent.includes("not_required")'))
        browser.screenshot(args.output / 'blocked-mobile.png',360,900)
        browser.call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':900,'deviceScaleFactor':1,'mobile':False})
        previous=browser.evaluate('selected')
        browser.evaluate('$("start").focus()'); browser.key('Enter',13)
        check('desktop-keyboard-blocked-campaign', browser.wait('selected!=='+json.dumps(previous)+' && $("evidence-verdict").textContent.includes("blocked")&&$("evidence-info").textContent.includes("not_required")',10))
        browser.evaluate('selected="physical";$("run-select").value=selected;epoch++;evidence()')
        # Data renders through textContent, including unusual source identities.
        check('untrusted-source-is-text', browser.evaluate('(()=>{const d=structuredClone(snapshot.diagnosis);d.observation.value={freshness_state:"unknown",observation:{source_session:"<img src=x onerror=window.pwned=true>"}};diagnose(d);return !window.pwned&&!$("source-info").querySelector("img")&&$("source-info").textContent.includes("<img");})()'))
        check('restore-actual-snapshot', browser.evaluate('diagnose(snapshot.diagnosis);true'))
        browser.call('Network.enable'); browser.call('Network.emulateNetworkConditions', {'offline':True,'latency':0,'downloadThroughput':0,'uploadThroughput':0})
        check('dashboard-loss-labelled-within-five-seconds', browser.wait('$("connection").textContent.includes("unavailable") && $("freshness").dataset.state==="unknown" && $("start").disabled', 5))
        browser.call('Network.emulateNetworkConditions', {'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1})
        check('reconnect-retains-selected-run', browser.wait('$("connection").textContent.includes("connected") && selected==="physical" && $("evidence-verdict").textContent.includes("passed")'))
        check('no-external-ui-dependencies', browser.evaluate('performance.getEntriesByType("resource").every(r=>r.name.startsWith(location.origin+"/"))'))
        check('no-javascript-errors', not browser.errors)
        record = {'status':'passed','scope':'Actual Chromium UI with live unavailable diagnosis and real registered historical reports; not human walkthrough', 'checks': checks,'javascript_errors':browser.errors}
    except Exception as error:
        record = {'status':'failed','error':str(error),'checks':checks}
    finally:
        if browser: browser.close()
    (args.output / 'verification.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record)); return 0 if record['status']=='passed' else 1


if __name__ == '__main__': raise SystemExit(main())
