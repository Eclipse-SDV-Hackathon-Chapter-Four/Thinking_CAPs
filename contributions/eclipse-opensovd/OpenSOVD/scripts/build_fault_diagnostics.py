#!/usr/bin/env python3
"""Build the optional native fault profile using an audited upstream patch and separate lock."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

REPO = Path(__file__).resolve().parents[4]
PIN = "12dac502616701734f90a61edca1326ae2ac6506"
URL = "https://github.com/eclipse-opensovd/fault-lib.git"


def run(command, timeout=600):
    return subprocess.check_output([str(value) for value in command], stderr=subprocess.STDOUT, timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=REPO / "OpenSOVD/.local/fault-build")
    parser.add_argument("--fault-source", type=Path)
    parser.add_argument("--target-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Run native integration tests and warnings-as-errors Clippy")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    args.state = args.state.resolve()
    args.state.mkdir(parents=True, exist_ok=True, mode=0o700)
    args.state.chmod(0o700)
    patch = REPO / "contributions/eclipse-opensovd/OpenSOVD/patches/fault-storage/write-through.patch"
    source = args.fault_source.resolve() if args.fault_source else args.state / "upstream"
    try:
        if not source.exists():
            run(["git", "clone", "--no-checkout", URL, source])
            run(["git", "-C", source, "checkout", "--detach", PIN])
            run(["git", "-C", source, "apply", patch])
        if run(["git", "-C", source, "rev-parse", "HEAD"]).decode().strip() != PIN:
            raise RuntimeError("fault source base revision differs from pin")
        if run(["git", "-C", source, "diff", "--binary", "HEAD"]) != patch.read_bytes():
            raise RuntimeError("fault source differs from the exported patch")
        if run(["git", "-C", source, "ls-files", "--others", "--exclude-standard"]).strip():
            raise RuntimeError("untracked upstream inputs require explicit review")
        # Compile a private source copy with its own lock. Default Cargo.lock keeps
        # immutable upstream Git sources; feature lock resolves the audited local patch.
        build_root = args.state / "source"
        package = build_root / "contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics"
        package.mkdir(parents=True, exist_ok=True)
        if (package / "src").exists():
            if not (build_root / ".sdv-owned-build").exists():
                raise RuntimeError("refuse replacing an unowned build source directory")
            shutil.rmtree(package / "src")
            shutil.rmtree(package / "tests")
        (build_root / ".sdv-owned-build").touch()
        origin = REPO / "contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics"
        shutil.copytree(origin / "src", package / "src")
        shutil.copytree(origin / "tests", package / "tests")
        shutil.copyfile(origin / "Cargo.toml", package / "Cargo.toml")
        shutil.copyfile(origin / "fault-build.lock", package / "Cargo.lock")
        catalog = build_root / "contributions/eclipse-opensovd/OpenSOVD/config/faults"
        catalog.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / "contributions/eclipse-opensovd/OpenSOVD/config/faults/cruise-control.json", catalog / "cruise-control.json")
        config = args.state / "build-config.toml"
        config.write_text('[patch."' + URL + '"]\n' + ''.join(
            name + ' = { path = ' + json.dumps(str(source / "src" / name)) + ' }\n'
            for name in ("common", "fault_lib", "dfm_lib")))
        command = ["cargo", "+stable", "build", "--locked", "--manifest-path", package / "Cargo.toml",
                   "--features", "fault-lifecycle", "--config", config, "--target-dir", args.target_dir.resolve()]
        (args.output / "build.txt").write_bytes(run(command))
        if args.check:
            for action, extra in (("test", []), ("clippy", ["--all-targets", "--", "-D", "warnings"])):
                check_command = command.copy()
                check_command[2] = action
                (args.output / (action + ".txt")).write_bytes(run(check_command + extra))
        binary = args.target_dir.resolve() / "debug/sdv-receiver-diagnostics"
        inputs = [origin / "Cargo.toml", origin / "Cargo.lock", origin / "fault-build.lock", patch,
                  REPO / "contributions/eclipse-opensovd/OpenSOVD/config/faults/cruise-control.json", *sorted((origin / "src").glob("*.rs"))]
        manifest = {"schema_version": 1, "work_classification": "prepared", "fault_lib_base": PIN,
                    "fault_lib_patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
                    "rust_kvs": "5d9f8225aa5622f52a31003bec937d5ef227dba7", "iceoryx2": "eba5da4b8d8cb03bccf1394d88a05e31f58838dc",
                    "rustc": run(["rustc", "+stable", "--version"]).decode().strip(), "native_faults": False,
                    "binary": str(binary), "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                    "inputs": {str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}}
        (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        (args.output / "results.json").write_text(json.dumps({"status": "passed", "checks": args.check}) + "\n")
        print(json.dumps({"status": "passed", "binary": str(binary)}))
        return 0
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        if isinstance(error, subprocess.CalledProcessError):
            (args.output / "failure.txt").write_bytes(error.output)
        (args.output / "results.json").write_text(json.dumps({"status": "failed", "reason": str(error)}) + "\n")
        print(json.dumps({"status": "failed", "reason": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
