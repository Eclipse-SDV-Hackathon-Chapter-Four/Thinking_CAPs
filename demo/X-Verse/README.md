# autoverse

## Prerequisites

- OS
  - Ubuntu 22.04

- Git
  - Registering SSH keys to GitHub is preferable.

## Set Up Tools

```bash
sudo apt update
sudo apt install -y git python3-pip
```

```bash
pip install --user rust-just vcstool
```

```bash
pip install --user evdev
```

### If you have troubles to install just in Ubuntu 22.04:

#### Setting up Prebuilt-MPR

Run the following to set up the APT repository on your system:
```bash
wget -qO - 'https://proget.makedeb.org/debian-feeds/prebuilt-mpr.pub' | gpg --dearmor | sudo tee /usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg 1> /dev/null
echo "deb [arch=all,$(dpkg --print-architecture) signed-by=/usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg] https://proget.makedeb.org prebuilt-mpr $(lsb_release -cs)" | sudo tee /etc/apt/sources.list.d/prebuilt-mpr.list
sudo apt update
```

#### Install just using apt
```bash
sudo apt install just
```

## Clone Repository (in $HOME folder)

```bash
git clone git@github.com:The-Xverse/autoverse.git && cd ~/autoverse
```

## Set Up Workspace

```bash
$ vcs import . < autoverse.repos
...........
=== ./bridges/can (git) ===
Cloning into '.'...
=== ./bridges/carla (git) ===
Cloning into '.'...
=== ./bridges/ros2 (git) ===
Cloning into '.'...
=== ./bridges/someip (git) ===
Cloning into '.'...
=== ./core/BCM (git) ===
Cloning into '.'...
=== ./core/zenoh (git) ===
Cloning into '.'...
=== ./vecu/bcm_can (git) ===
Cloning into '.'...
=== ./vecu/s-core (git) ===
Cloning into '.'...
=== ./vecu/simulink (git) ===
Cloning into '.'...
=== ./vecu/vcu_can (git) ===
Cloning into '.'...
=== ./vecu/vcu_zenoh (git) ===
Cloning into '.'...
```

<br>

> [!NOTE]
> Whenever you need to modify the tracking repo's versions/branches, dispite the vcs import command, the vcs pull command (as follow) should also be executed after, in order to apply the new versions/branches tracking to repos. <br>
> ```
> vcs pull --nested
> ```

## Set Up Environment

### CARLA Simulator & Eclipse Zenoh

```bash
$ just
Available recipes:
    [Carla Build]
    build-libcarla                                  # Build CARLA API (C++)
    make-carla                                      # Build CARLA API (Rust)

    [Carla Client]
    install-client                                  # Install the CARLA Python API
    run-automatic host="127.0.0.1" port="2000"      # Run automatic control with Zenoh
    run-manual router="127.0.0.1" host="127.0.0.1" port="2000" # Run manual control with Zenoh
    run-manual-steering router="127.0.0.1" host="127.0.0.1" port="2000" fullscreen="false" # Run Steering control with Zenoh
    run-manual-steering-carla-mock router="127.0.0.1" host="127.0.0.1" port="2000" fullscreen="false" # Run Steering control with Zenoh
    run-manual-steering-sync router="127.0.0.1" host="127.0.0.1" port="2000" fullscreen="false" # Run Steering control with Zenoh
    setup-g920-steer                                # Setup persistent Logitech G920 device
    uninstall-client                                # Uninstall CARLA Python API

    [Carla Server]
    install-server                                  # Install the CARLA Simulator
    server-nvidia quality="Epic" port="2000"        # Run CARLA off-screen using NVIDIA card
    server-offscreen quality="Epic" port="2000"     # Run CARLA in off-screen mode
    server-windowed quality="Epic" port="2000"      # Run CARLA in windowed mode
    uninstall-server                                # Uninstall CARLA Simulator

    [Distrobox]
    create-container name                           # Create an Ubuntu 22.04 container
    enter-container name                            # Enter the container
    remove-container name                           # Remove the container

    [Rust]
    install-rust                                    # Install the Rust Language tools
    run-workspace                                   # Run a demo project (bin + lib) in Rust
    uninstall-rust                                  # Uninstall Rust Language

    [Utilities]
    check-host expected="ubuntu"                    # Check current host
    fix-wsl                                         # Fix WSL permission issues

    [Virtual Vehicle Module]
    run-vehicle-manual-control router="192.168.1.102" host="192.168.1.102" port="2000" # Run Vehicle Manual Control on Premisses with Zenoh Integration
    run-virtual-vehicle-on-cloud *FLAGS             # Run Virtual Vehicle on Cloud with Zenoh Integration

    [Zenoh]
    install-zenoh                                   # Install the Zenoh Python API
    run-publisher key payload iter="1" interval="1" # Run generic publisher
    run-subscriber key                              # Run generic subscriber
    uninstall-zenoh
```

### Verify Environment

```bash
just check-host
```

### Troubleshooting

If you are using WSL, you may face the following error when running the `check-host` command.

```bash
$ just check-host
error: Recipe `_check_host` with shebang `#!/usr/bin/env -S bash -x` execution error: Permission denied (os error 13)
error: Recipe `check-host` failed on line 64 with exit code 1
```

To fix that, please run the following commands before proceeding.

```bash
just fix-wsl && source ~/.bashrc
```

Then run 'check-host' again and check if you get the same output below. If so, you are ready to proceed.

```bash
$ just check-host

You are running on host 'ubuntu'.
```

### Zenoh

#### Install

```bash
just install-zenoh
```

#### Test (Terminal #1)

```bash
just run-publisher demo/example/test 'Hello World' 10 1.0
```

#### Test (Terminal #2)

```bash
just run-subscriber 'demo/**'
```
<br>

---
> [!NOTE]
> **CARLA Server** and **CARLA Client** sections are only applicable for a PC with dedicated GPU intended to run CARLA Simulator. <br>
> For CARLA mock implementation usage, only the **CARLA Client** section is applicable, once it sets up a regular PC without GPU to run it.
---

<br>

### CARLA Server

#### Install

```bash
just install-server
```

#### Test

```bash
just server-windowed
```

### CARLA Client

#### Install

```bash
just install-client
```

#### Test (Terminal #1)

```bash
just server-offscreen
```

#### Test (Terminal #2)

```bash
just run-automatic
```

<br>

---
> [!NOTE]
> **Rust Language** section is not currently applicable and has been kept only for reference and future use.
---

<br>

### Rust Language

#### Install

```bash
just install-rust
```

#### Test

```bash
just run-workspace
```

#### Uninstall

```bash
just uninstall-rust
```

---

## Cruise Control Use Case

### Autoverse Supervisor

The `run_autoverse.py` script is a process supervisor that automatically manages and orchestrates all Autoverse modules in a single command.

#### What it does

- **Automatic startup**: Launches CARLA Server, Communication Bridges, VCU, ADAS, Vehicle Manual Control and Virtual Vehicle modules in the correct order
- **Process management**: Monitors all modules and handles graceful shutdown
- **Clean environment**: Kills stale processes before starting
- **Multi-monitor support**: Automatically places CARLA Simulation window on secondary monitor
- **Centralized logging**: Stores all logs in `~/.cache/autoverse-runner/logs`

#### Command-line Options

| Option | Description | Note |
|--------|-------------|------|
| `--only-zenoh-modules` | Use Zenoh-based VCU and PID Controller | Lightest and lean deploy mode |
| `--vuc-zenoh` | Use VCU Zenoh-based version | Lightweight deploy mode to use together with SOME/IP modules |
| `--carla-mock` | Run without CARLA Server | Testing mode, no GPU required |
| `--enable-camera-display`* | Enable camera rendering (mutually exclusive with `--carla-mock`) | *Temporarily disabled, it's being set to True internally by default |
| `-h, --help` | Show help message | - |

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AUTOVERSE_DISPLAY_NAME` | Preferred monitor name (e.g., "HDMI-0") | Auto-detect |
| `AUTOVERSE_DISPLAY_INDEX` | Preferred monitor index (0-based) | Auto-detect |
| `CARLA_PORT` | CARLA RPC port | 2000 |
| `CARLA_STREAMING_PORT` | CARLA streaming port | 2001 |

#### Stopping the Supervisor

Press `Ctrl+C` to gracefully stop all modules. The supervisor will:
1. Terminate all child processes
2. Kill any remaining CARLA Server instances
3. Clean up resources

#### Logs

All module logs are stored in:
```
~/.cache/autoverse-runner/logs/
```

Each module has separate stdout and stderr log files with timestamps.


#### Usage and deployment modes

<br>

> [!NOTE]
> Since the `--enable-camera-display` arg is temporarily disabled, please consider that all deployment modes are using this arg by default, meaning that the CARLA Camera display will be deployed locally.
>

##### Full setup with Zenoh, SOME/IP and CAN modules with headless display (regular mode)

Placeholder for hybrid deployment where some modules running on premisses and others on Cloud

```bash
python3 run_autoverse.py
```

This starts:
1. CARLA Server (NVIDIA)
2. Zenoh to SOME/IP bridge container
2. Zenoh to CAN bridge (placeholder to be validated)
3. ADAS Module (s-core C++ container)
4. Vehicle Manual Control
5. Virtual Vehicle Module using CARLA Client with headless display via automate.py

###### Adding `--enable-camera-display` arg

```bash
python3 run_autoverse.py --enable-camera-display
```

This starts:
Steps 1 to 4 are the same.
5. Virtual Vehicle Module using CARLA Client with camera display rendering via automate.py
*Enables PyGame camera display rendering (cannot be used with `--carla-mock`).


##### Lean setup for local deployment

###### Full simulation using CARLA Simulator Server, but with only zenoh modules

```bash
python3 run_autoverse.py --only-zenoh-modules
```

This starts:
1. CARLA Server (NVIDIA)
2. VCU Module (Python Zenoh)
3. ADAS Module (PID Controller Python Zenoh)
4. Vehicle Manual Control
5. Virtual Vehicle Module using CARLA Client with headless display via automate.py

**Adding `--enable-camera-display` arg**

```bash
python3 run_autoverse.py --only-zenoh-modules --enable-camera-display
```

This starts:
Steps 1 to 4 are the same.
5. Virtual Vehicle Module using CARLA Client with camera display rendering via automate.py
*Enables PyGame camera display rendering (cannot be used with `--carla-mock`).


###### Full simulation using CARLA Simulator Server, but with VCU Zenoh module

```bash
python3 run_autoverse.py --vcu-zenoh
```

This starts:
1. CARLA Server (NVIDIA)
2. VCU Module (Python Zenoh)
3. Zenoh to SOME/IP bridge container
3. Zenoh to CAN bridge (placeholder to be validated)
4. ADAS Module (s-core C++ container)
5. Vehicle Manual Control
6. Virtual Vehicle Module using CARLA Client with headless display via automate.py

**Adding `--enable-camera-display` arg**

```bash
python3 run_autoverse.py --vcu-zenoh --enable-camera-display
```

This starts:
Steps 1 to 5 are the same.
6. Virtual Vehicle Module using CARLA Client with camera display rendering via automate.py
*Enables PyGame camera display rendering (cannot be used with `--carla-mock`).

###### CARLA Mock implementation (No GPU Required)

**Zenoh, SOME/IP and CAN modules deployment**

```bash
python3 run_autoverse.py --carla-mock
```

Runs without actual CARLA Simulator Server - useful for testing on machines without GPU.

This starts:
1. Zenoh to SOME/IP bridge container
1. Zenoh to CAN bridge (placeholder to be validated)
2. ADAS Module (s-core C++ container)
3. Vehicle Manual Control
4. Virtual Vehicle Module using CARLA Mock via automate.py


**Adding `--only-zenoh-modules` arg**

```bash
python3 run_autoverse.py --carla-mock --only-zenoh-modules
```

This starts:
1. VCU Module (Python Zenoh)
2. ADAS Module (PID Controller Python Zenoh)
3. Vehicle Manual Control
4. Virtual Vehicle Module using CARLA Mock via automate.py


**Adding `--vcu-zenoh` arg**

```bash
python3 run_autoverse.py --carla-mock --vcu-zenoh
```

This starts:
1. VCU Module (Python Zenoh)
2. Zenoh to SOME/IP bridge container
2. Zenoh to CAN bridge (placeholder to be validated)
3. ADAS Module (s-core C++ container)
4. Vehicle Manual Control
5. Virtual Vehicle Module using CARLA Mock via automate.py


### Stand-alone deployment with only Zenoh Modules (bare minimum setup)

#### Run Carla Server (Terminal #1)

```bash
just server-offscreen low
```

#### Run Vehicle Manual Control module (Terminal #2)

```bash
just run-vehicle-manual-control
```

#### Run Virtual Vehicle module (Terminal #3)

Choose between the different deployment modes:

##### CARLA Client with Camera Display rendering (only for PCs with GPU)

```bash
just run-virtual-vehicle-on-cloud --enable-camera-display
```

##### CARLA Client with headless display mode (only for PCs with GPU)

```bash
just run-virtual-vehicle-on-cloud
```

##### CARLA Mock implementation with debug GUI (doesn't require GPU)

Runs Vehicle simulation without actual CARLA Simulator Server - useful for testing on machines without GPU.

```bash
just run-virtual-vehicle-on-cloud --carla-mock
```

#### Run ADAS - PID Controller (Terminal #4)

```bash
python3 vecu/simulink/pid_controller/main.py
```

#### Run VCU Python Zenoh (Terminal #5)

```bash
python3 vecu/vcu_zenoh/src/main.py
```
