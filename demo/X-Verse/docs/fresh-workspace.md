# Recreate the current integration in a fresh workspace

Use this procedure to check out and build the integration in a fresh workspace. It starts with new source checkouts, Python environments, native build outputs, bench state and dashboard state. It uses an existing Ubuntu 22.04 host with Docker, Git LFS, KVM, NVIDIA/Vulkan and Rust installed. It does not require a previously compiled controller or diagnostic binary.

Keep the interactive baseline and other instances of this bench stopped. Only one bench can use the selected management subnet and port 7447. Choose a Linux filesystem that supports symbolic links and executable permissions, with at least 60 GB free. Follow step 9 for the full supervisor's container settings and home-relative recipes.

Keep at least 10 GB free **after** all builds and extraction, before each Android
start or resume. Cuttlefish checks capacity for its 8 GB userdata image on
restart, even when the existing image is sparse. Check with
`df -h "$SDV_WORKSPACE"`; do not estimate headroom from extracted file sizes.

## 1. Obtain the current sources

Install the host prerequisites listed in the main README first. Choose a workspace directory with no existing component checkouts. Clone the published branches and import the component versions selected by `autoverse.repos`:

```bash
export SDV_WORKSPACE="${SDV_WORKSPACE:-$HOME/sdv-workspace}"
mkdir -p "$SDV_WORKSPACE"
export PATH="$HOME/.local/bin:/usr/bin:$PATH"
/usr/bin/python3 -m pip install --user vcstool
git lfs install

cd "$SDV_WORKSPACE"
git clone --branch dev/sdv-hackathon-2026 \
  git@github.com:The-Xverse/autoverse.git
git clone --branch contributions/eclipse-sdv-hackathon \
  git@github.com:The-Xverse/eclipse_sdv_hackathon_2026.git
cd "$SDV_WORKSPACE/autoverse"
vcs import . < autoverse.repos
vcs status
```

The manifest selects all 11 component repositories. Git LFS objects require access to their remotes. Keep the selected source revisions with your build results. For a frozen source handoff, `tools/export_source_package.py` can optionally export Git bundles and a checksummed manifest from an existing workspace.

## 2. Install fresh Python dependencies and CARLA

```bash
cd "$SDV_WORKSPACE/eclipse_sdv_hackathon_2026"
/usr/bin/python3 -m venv .venv
export LAB_PYTHON="$PWD/.venv/bin/python"
"$LAB_PYTHON" -m pip install -r requirements-carla.txt
"$LAB_PYTHON" -m pip install -r "$SDV_WORKSPACE/autoverse/requirements.txt"
"$LAB_PYTHON" -c 'import carla, pygame, numpy, zenoh, psutil; print("Vehicle dependencies ready")'

if [[ ! -f "$SDV_WORKSPACE/CARLA_0.9.15.tar.gz" ]]; then
  curl --fail --location --retry 3 \
    https://downloads.carlasim.com/Linux/CARLA_0.9.15.tar.gz \
    --output "$SDV_WORKSPACE/CARLA_0.9.15.tar.gz.part"
  mv "$SDV_WORKSPACE/CARLA_0.9.15.tar.gz.part" "$SDV_WORKSPACE/CARLA_0.9.15.tar.gz"
fi
printf '%s\n' "32fa681fb925cd62951a63977582ea8c  $SDV_WORKSPACE/CARLA_0.9.15.tar.gz" | md5sum --check
mkdir "$SDV_WORKSPACE/carla-simulator"
tar -xf "$SDV_WORKSPACE/CARLA_0.9.15.tar.gz" -C "$SDV_WORKSPACE/carla-simulator"
```

Do not start this server manually. The physical campaign owns ports 2100–2102 and starts it itself.

You can reuse a downloaded vendor installer by copying it to `"$SDV_WORKSPACE/CARLA_0.9.15.tar.gz"` before this step. The checksum is verified before extraction.

## 3. Build native runtime and development images

Choose a unique tag prefix and keep it set in this terminal:

```bash
export LAB_TAG="${LAB_TAG:-sdv-lab-$(date +%s)}"
export LAB_DIR="${LAB_DIR:-$SDV_WORKSPACE/lab}"
mkdir -p "$LAB_DIR"

cd "$SDV_WORKSPACE/autoverse/bridges/someip/zenoh-someip-bridge"
git lfs pull
docker build -t "$LAB_TAG-bridge" -f docker/Dockerfile .
docker run --rm "$LAB_TAG-bridge" ctest --test-dir build --output-on-failure

cd "$SDV_WORKSPACE/autoverse/vecu/s-core/cc_s-core"
docker build -t "$LAB_TAG-score" -f deployment/xverse/docker_setup/Dockerfile .
cd "$SDV_WORKSPACE/autoverse/vecu/s-core"
docker build -t "$LAB_TAG-build" .devcontainer
```

Both bridge test suites must pass before continuing.

## 4. Create the cache and native build configuration

Provision the LLVM 19.1.0 repository required by the pinned S-CORE toolchain. It must contain `BUILD.bazel`, `bin/clang` and the associated libraries. Set `SDV_LLVM_SOURCE` to its location on your machine. The commands copy the compiler into a new cache; native application outputs are built in the next step.

```bash
export SDV_LLVM_SOURCE=/absolute/path/to/llvm-19.1.0-repository
test -f "$SDV_LLVM_SOURCE/BUILD.bazel"
"$SDV_LLVM_SOURCE/bin/clang" --version
mkdir "$LAB_DIR/bazel-cache"
cp -a "$SDV_LLVM_SOURCE" "$LAB_DIR/bazel-cache/llvm"
export LAB_BAZEL_VOLUME="$LAB_TAG-bazel"
docker volume create --driver local \
  --opt type=none --opt o=bind --opt "device=$LAB_DIR/bazel-cache" "$LAB_BAZEL_VOLUME"
rustc +stable --version

"$LAB_PYTHON" - <<'PY'
import json, os, subprocess
from pathlib import Path
workspace = Path(os.environ['SDV_WORKSPACE']).resolve()
lab = Path(os.environ['LAB_DIR']).resolve()
tag = os.environ['LAB_TAG']
def image(suffix):
    return subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}', tag + suffix], text=True).strip()
bridge = workspace / 'autoverse/bridges/someip/zenoh-someip-bridge'
config = {
    'schema_version': 1, 'state': str(lab / 'bench'),
    'baseline_source': str(workspace / 'autoverse/vecu/s-core/cc_s-core'),
    'bridge_source': str(bridge),
    'bridge_revision': subprocess.check_output(['git', '-C', str(bridge), 'rev-parse', 'HEAD'], text=True).strip(),
    'score_image': image('-score'), 'bridge_image': image('-bridge'), 'score_build_image': image('-build'),
    'bazel_volume': os.environ['LAB_BAZEL_VOLUME'], 'llvm_repository': '/var/cache/bazel/llvm',
    'expected_rustc': subprocess.check_output(['rustc', '+stable', '--version'], text=True).strip(),
    'carla': {
        'root': str(workspace / 'carla-simulator'), 'port': 2100,
        'vehicle_module': str(workspace / 'autoverse/bridges/carla/examples/virtual_vehicle.py'),
        'signals': str(workspace / 'autoverse/bridges/carla/examples/signals_config.json'),
        'vcu_module': str(workspace / 'autoverse/vecu/vcu_zenoh/src/controller.py'),
        'seed': 42, 'vulkan_icd': '/usr/share/vulkan/icd.d/nvidia_icd.json', 'startup_timeout_seconds': 120,
    },
}
(lab / 'campaign.json').write_text(json.dumps(config, indent=2) + '\n')
PY
```

The native profile was validated with Rust 1.98.1. The selected compiler identity is recorded for reproduction. `OpenSOVD/integration/diagnostics/fault-build.lock` pins Cargo dependencies; the fault-build helper uses this lock for the selected profile.

## 5. Deploy a new openDuT bench and compile the integration

```bash
cd "$SDV_WORKSPACE/eclipse_sdv_hackathon_2026"
"$LAB_PYTHON" OpenDut/scripts/opendut_testbench.py prepare --state "$LAB_DIR/bench" --output "$LAB_DIR/bench-prepare"
"$LAB_PYTHON" OpenDut/scripts/opendut_testbench.py up --state "$LAB_DIR/bench" --output "$LAB_DIR/bench-up"
"$LAB_PYTHON" scripts/reproduce_core.py --config "$LAB_DIR/campaign.json" \
  --state "$LAB_DIR/native-build" --output "$LAB_DIR/reproduction" \
  --operator 'README reproduction'
cp "$LAB_DIR/reproduction/reproduction-inputs.json" "$LAB_DIR/campaign.json"
"$LAB_PYTHON" -B -m unittest discover -s tests -p 'test_*.py' -v
```

The reproduction must report `passed`, including the native core campaign. It freezes the selected committed source revisions, builds a new controller and diagnostic/fault provider, runs unit checks and Clippy, and generates actual compiler, binary and source paths. Do not substitute old binaries when a build fails.

## 6. Start the web UI and exercise the physical campaign

```bash
cd "$SDV_WORKSPACE/eclipse_sdv_hackathon_2026"
"$LAB_PYTHON" - <<'PY'
import json, os
from pathlib import Path
lab = Path(os.environ['LAB_DIR']).resolve()
config = {'schema_version': 1, 'state_dir': str(lab / 'dashboard-state'),
          'campaign_config': str(lab / 'campaign.json'), 'python': os.environ['LAB_PYTHON'],
          'diagnostic_base': 'http://172.30.77.12:7691/sovd', 'historical': []}
(lab / 'dashboard.json').write_text(json.dumps(config, indent=2) + '\n')
PY
"$LAB_PYTHON" scripts/run_dashboard.py --config "$LAB_DIR/dashboard.json" --port 8791
```

Open `http://127.0.0.1:8791`. Follow the main README's [physical campaign walkthrough](../README.md#5-exercise-the-agreed-scenario): connected peers, start, live native diagnosis, link loss, recovery, verified evidence downloads, deliberate-failure restoration, and cancellation. Wait for Start to become enabled between runs. Cancellation during application startup uses the actual application resource inventory; incomplete cleanup evidence still blocks another run.

The collector-loss check abruptly stops the receiver container while publication continues. This isolates collector unavailability from a graceful stack shutdown, which can interrupt SOME/IP while the receiver is still reporting. Native diagnostic SIGINT and SIGTERM shutdown are verified separately.

After completing the browser checks and confirming no campaign remains active,
stop the foreground dashboard with Ctrl+C. Continue in this same terminal so
the exported workspace and lab variables remain available.

## 7. Verify Android separately before the complete baseline

The selected diagnostic campaigns do not require Android. To validate the full baseline's Android prerequisite from this same fresh checkout:

```bash
cd "$SDV_WORKSPACE/autoverse/vecu/aaos_cuttlefish"
export IMAGE="$LAB_TAG-android"
export CONTAINER="$LAB_TAG-android"
export CUTTLEFISH_OPEN_BROWSER=0
./ctl.sh make
./ctl.sh start
timeout 10 adb -s localhost:6520 shell getprop sys.boot_completed
adb -s localhost:6520 shell pm list packages | rg com.example.digitalclusterapp
./ctl.sh stop
```

`start` uses explicit artifact/state paths, enables the serial console, waits up to 300 seconds for boot completion and installs the APK with the selected ADB serial. Boot completion must print `1`, installation must report `Success`, and the package must be present. Logs are in `runtime/cvd_launch.log` and `runtime/cvd-state/instances/cvd-1/logs/`. `CUTTLEFISH_OPEN_BROWSER=0` suppresses automatic browser opening; the HTTPS viewer remains available at `https://localhost:8443` while running.

## 8. Stop the owned test services

With the dashboard stopped, use the terminal retaining the lab variables:

```bash
cd "$SDV_WORKSPACE/eclipse_sdv_hackathon_2026"
"$LAB_PYTHON" OpenDut/scripts/opendut_testbench.py down --state "$LAB_DIR/bench" --output "$LAB_DIR/bench-down"
```

Keep source revisions, logs and failed or passing run artifacts. Bench teardown is separate from a campaign's recorded cleanup verdict. Follow the baseline provisioning steps in the main README before using `python3 run_autoverse.py --enable-camera-display --vcu-zenoh`; the integration dashboard is not a substitute for that command's full vehicle/Android provisioning.

## 9. Prepare and check the complete supervisor

Run this after bench teardown, with other supervisors stopped and CARLA ports 2000–2002 free. For a checkout outside `~/autoverse`, the workspace wrapper uses Bubblewrap to provide the home-relative paths required by the recipes and permits the desktop's X11 connection. Install `bubblewrap` with the host prerequisites if needed.

```bash
export WORKSPACE_HOME_RUN="$SDV_WORKSPACE/autoverse/tools/ssd_home.sh"
"$WORKSPACE_HOME_RUN" "$SDV_WORKSPACE" /usr/bin/python3 -m pip install --user rust-just vcstool
"$WORKSPACE_HOME_RUN" "$SDV_WORKSPACE" bash -c 'export PATH="$HOME/.local/bin:/usr/bin:$PATH"; just install-zenoh; just install-client'
"$LAB_PYTHON" -m pip install evdev matplotlib shapely networkx

export AUTOVERSE_PYTHON="$LAB_PYTHON"
export AUTOVERSE_BRIDGE_IMAGE="$LAB_TAG-bridge"
export AUTOVERSE_BRIDGE_CONTAINER="$LAB_TAG-baseline-bridge"
export AUTOVERSE_ANDROID_IMAGE="$LAB_TAG-android"
export AUTOVERSE_ANDROID_CONTAINER="$LAB_TAG-android"
export CUTTLEFISH_OPEN_BROWSER=0
export COMPOSE_PROJECT_NAME="$LAB_TAG-baseline-score"
export SCORE_FOR=X-Verse
export SCORE_BAZEL_VOLUME="$LAB_BAZEL_VOLUME"
export SCORE_RUNTIME_IMAGE="$LAB_TAG-score"
export SOURCE_DIR="$LAB_DIR/native-build/score/cc_s-core"
unset IMAGE CONTAINER

cd "$SDV_WORKSPACE/autoverse/vecu/s-core"
./ctl.sh up
./ctl.sh stop
docker run --init --rm -d --name "$LAB_TAG-router" --network host eclipse/zenoh:1.3.4

"$WORKSPACE_HOME_RUN" "$SDV_WORKSPACE" bash -c 'export PATH="$HOME/.local/bin:/usr/bin:$PATH"; python3 run_autoverse.py --enable-camera-display --vcu-zenoh'
```

The component overrides apply different names/images to the bridge and Android; the S-CORE project uses the new native outputs and cache. The baseline still uses shared ports and process cleanup patterns: it cannot run concurrently with another supervisor or the managed campaign. Do not set the generic `IMAGE`/`CONTAINER` variables for this launch.

Confirm the camera and manual-control windows, a responsive CARLA actor, the running bridge and S-CORE containers, Android boot completion and the installed cluster. Open `https://localhost:8443` manually. Installation does not launch the cluster; open it from Android's app menu or run:

```bash
adb -s localhost:6520 shell am start \
  -a android.intent.action.MAIN -c android.intent.category.LAUNCHER \
  -p com.example.digitalclusterapp
```

Configure the cluster's Zenoh connection before checking its telemetry. Its
default `tcp/10.0.2.2:7447` is an Android Emulator address. Configure it using
the Cuttlefish guest's host gateway:

```bash
adb -s localhost:6520 shell ip route show table all
```

Use the gateway in the `default via` route for `buried_eth0`. In the cluster,
open the gear icon, select **client (router)**, set **Endpoint** to
`tcp/<gateway>:7447`, press **Save**, then
**Restart app**. The new endpoint is saved; sessions cannot be changed live.
The separately started Zenoh router must be running on the host.

Use the main README's keyboard driving checks in the Vehicle Manual Control
window and confirm the Android speed changes with the vehicle. A supervisor
process alone is insufficient. Stop with Ctrl+C, then stop the separately
launched router:

```bash
docker stop "$LAB_TAG-router"
```

Retain the workspace and logs. Do not start a managed campaign until the baseline and router have stopped.
