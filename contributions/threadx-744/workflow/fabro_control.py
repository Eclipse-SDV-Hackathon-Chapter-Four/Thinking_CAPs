#!/usr/bin/env python3
"""Operate the dedicated loop4 Fabro server without exposing authentication."""
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request

PACKAGE = Path(__file__).resolve().parent
ARTIFACTS = PACKAGE.parent / "artifacts"
STORE = Path("/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/threadx-contributions/fabro-storage")
SERVER = "http://127.0.0.1:32277/api/v1"


def request(path, payload=None):
    values = dict(line.split("=", 1) for line in (STORE / "server.env").read_text().splitlines() if "=" in line)
    req = urllib.request.Request(SERVER + path,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + values["FABRO_DEV_TOKEN"], "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode()
        raise RuntimeError(f"Fabro HTTP {error.code}: {body[:1500]}") from None


def save(name, value):
    ARTIFACTS.mkdir(exist_ok=True)
    (ARTIFACTS / name).write_text(json.dumps(value, indent=2) + "\n")


def launch():
    files = {str(p.relative_to(PACKAGE)): p.read_text() for p in PACKAGE.rglob("*")
             if p.is_file() and p.suffix in [".md", ".py", ".toml", ".fabro"]}
    files["Dockerfile"] = (PACKAGE / "Dockerfile").read_text()
    version = request("/workflow-versions", {"entrypoint": "workflow.fabro", "files": files, "workflow_dependencies": {}})
    save("workflow-version.json", version)
    run = request("/runs", {"workflow_version_id": version["workflow_version_id"],
          "target": {"kind": "folder", "path": "/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/threadx-contributions/744/source"},
          "environment_id": "local", "title": "ThreadX #744 — Codex Sol 6.1 High contribution",
          "args": {"labels": {"project": "eclipse-threadx", "issue": "744", "model": "gpt-6.1-sol", "reasoning": "high", "storage": "loop4"}}})
    save("fabro-run-created.json", run)
    run_id = run.get("id", run.get("run_id"))
    started = request("/runs/" + run_id + "/start", {})
    save("fabro-run-started.json", started)
    print(json.dumps({"run_id": run_id, "workflow_version_id": version["workflow_version_id"], "server": SERVER}))


if __name__ == "__main__":
    if sys.argv[1] == "launch":
        launch()
    else:
        run = json.loads((ARTIFACTS / "fabro-run-created.json").read_text())
        run_id = run.get("id", run.get("run_id"))
        result = request("/runs/" + run_id)
        save("fabro-run-status.json", result)
        print(json.dumps(result, indent=2))
