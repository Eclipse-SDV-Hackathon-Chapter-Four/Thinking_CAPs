#!/usr/bin/env python3
"""Serve the local OpenSOVD diagnosis and openDuT campaign dashboard."""
import argparse
import json
from pathlib import Path
import signal
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integration.dashboard.service import Dashboard, server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8787)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    app = Dashboard(config)
    httpd = None
    try:
        httpd = server(app, args.port)
        def shutdown(signum, frame):
            for sig in (signal.SIGINT, signal.SIGTERM): signal.signal(sig, signal.SIG_IGN)
            threading.Thread(target=httpd.shutdown, daemon=True).start()
        for sig in (signal.SIGINT, signal.SIGTERM): signal.signal(sig, shutdown)
        print(json.dumps({'url': 'http://127.0.0.1:' + str(httpd.server_port), 'classification': 'prepared',
                          'campaign_config': str(app.inputs)}), flush=True)
        httpd.serve_forever(poll_interval=.2)
    finally:
        if httpd: httpd.server_close()
        app.close()
    return 0


if __name__ == '__main__': raise SystemExit(main())
