# OpenAirInterface 5G - Emulated Mode Setup Guide

> **Platform Note**: This guide was tested on **Jetson Orin Nano** (ARM64). Most commands require `sudo` for Docker operations.

---

## Overview

This guide covers setting up **OAI 5G Standalone (SA)** in **emulated mode**, where the gNB and nrUE run as containers on the same machine, communicating through simulated RF channels via TCP instead of real radio hardware.

> **Emulated Mode vs Over-the-Air**: Emulated mode bypasses physical radio hardware, enabling development and testing without SDR equipment.

---

## Architecture

```mermaid
flowchart LR
    subgraph Core Network["Core Network (Docker)"]
        M["MySQL<br/>192.168.71.131"]
        A["AMF<br/>192.168.71.132"]
        S["SMF<br/>192.168.71.133"]
        U["UPF<br/>192.168.71.134<br/>192.168.72.134"]
        D["ext-dn<br/>192.168.72.135"]
    end

    subgraph Radio["RF Simulator"]
        G["gNB Container<br/>192.168.71.140<br/>--rfsim"]
        R["RF Simulator<br/>TCP 4043"]
        Ue["nrUE Container<br/>192.168.71.150<br/>--rfsim"]
    end

    G <-->|TCP 4043| R <-->|TCP 4043| Ue
    G --> A
    Ue --> A
    A --> S --> U --> D
    Ue -.->|Tunnel<br/>12.1.1.2| U
```

### Network Addressing

| Component | IP Address |
|-----------|------------|
| MySQL | 192.168.71.131 |
| AMF | 192.168.71.132 |
| SMF | 192.168.71.133 |
| UPF (N3) | 192.168.71.134 |
| UPF (N6) | 192.168.72.134 |
| ext-dn | 192.168.72.135 |
| gNB | 192.168.71.140 |
| nrUE | 192.168.71.150 |
| UE Tunnel | 12.1.1.2 |

### Key Parameters

| Parameter | Value |
|-----------|-------|
| PLMN | 208.99 |
| DNN | oai |
| NSSAI SST | 1 |
| UE IMSI | 208990100001100 |
| gNB PRB | 106 |
| Numerology | 1 (15 kHz subcarrier spacing) |
| Center Frequency | 3319680000 Hz (3.32 GHz) |

---

## Prerequisites

### Hardware Requirements

- **Jetson Orin Nano** (or similar ARM64 board) or x86_64 desktop
- **CPU**: 8 cores ARM64/x86_64 @ 3.5 GHz
- **RAM**: 32 GB (8 GB minimum for containers)
- **Storage**: 50+ GB free space

### Software Requirements

- **Docker**: Version 20.10+ with docker-compose plugin
- **Git**: For cloning repositories

### Important: Sudo Access Required

> **All Docker commands require `sudo` on most systems.**

Add your user to the docker group to avoid sudo:
```bash
sudo usermod -aG docker $USER
newgrp docker
# Or logout/login for changes to take effect
```

---

## Setup

### Step 1: Create Working Directory

```bash
mkdir -p ~/oai
cd ~/oai
```

### Step 2: Clone OAI Repository

```bash
git clone https://gitlab.eurecom.fr/oai/openairinterface5g.git ~/openairinterface5g
cd ~/openairinterface5g
git checkout develop
```

### Step 3: Navigate to RF Simulator Config

```bash
cd ~/openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator
```

### Step 4: Pull Docker Images

```bash
sudo docker compose pull
```

> **Note**: This downloads ~2GB of data and may take 10-20 minutes depending on your connection.

Verify images are present:

```bash
sudo docker images | grep oai
```

Expected output:
```
oaisoftwarealliance/oai-amf      develop
oaisoftwarealliance/oai-smf      develop
oaisoftwarealliance/oai-upf      develop
oaisoftwarealliance/oai-gnb      develop
oaisoftwarealliance/oai-nr-ue    develop
oaisoftwarealliance/oai-nrf      develop
oaisoftwarealliance/oai-ausf     develop
oaisoftwarealliance/oai-udm      develop
oaisoftwarealliance/oai-udr      develop
```

---

## Running Emulated Mode

### Start Core Network

```bash
sudo docker compose up -d mysql oai-amf oai-smf oai-upf oai-ext-dn
```

Wait for containers to become healthy:

```bash
sleep 20
```

### Start gNB

```bash
sudo docker compose up -d oai-gnb
```

Wait for gNB to initialize:

```bash
sleep 10
```

### Start nrUE

```bash
sudo docker compose up -d oai-nr-ue
```

---

## Verification

### Check Container Status

```bash
sudo docker compose ps
```

All containers should show status `healthy`:

```
NAME                 STATUS
rfsim5g-mysql        healthy
rfsim5g-oai-amf      healthy
rfsim5g-oai-smf      healthy
rfsim5g-oai-upf      healthy
rfsim5g-oai-ext-dn   healthy
rfsim5g-oai-gnb      healthy
rfsim5g-oai-nr-ue    healthy
```

### Check gNB Connection

```bash
sudo docker logs rfsim5g-oai-gnb 2>&1 | grep -i "connected\|rfsim"
```

Expected: Look for `RFSIMULATOR` device loaded and UE connections.

### Check nrUE Registration

```bash
sudo docker logs rfsim5g-oai-nr-ue 2>&1 | grep -i "NR_RRC_CONNECTED\|registered"
```

Expected: `NR_RRC_CONNECTED` state reached.

### Check Network Interfaces Inside nrUE

```bash
sudo docker exec rfsim5g-oai-nr-ue ifconfig -a
```

Look for `oaitun_ue1` interface - this is created only after successful registration.

### Test Connectivity (After Tunnel Appears)

```bash
sudo docker exec rfsim5g-oai-nr-ue ping -I oaitun_ue1 -c 5 192.168.72.135
```

Expected output:
```
5 packets transmitted, 5 received, 0% packet loss
rtt min/avg/max = X/Y/Z ms
```

> **Note**: The `oaitun_ue1` tunnel interface is created by the nrUE software **only after**:
> 1. RRC connection is established with gNB
> 2. NAS authentication succeeds with AMF
> 3. PDU session is established
>
> If `oaitun_ue1` doesn't appear, check the logs for registration failures.

---

## Understanding the Components

### What is RFSIM?

The **RF Simulator (RFSIM)** is a software component that simulates the radio frequency channel between gNB and nrUE using TCP sockets instead of actual RF hardware.

Key characteristics:
- Runs gNB and nrUE on the **same machine** (or different machines via network)
- Simulates channel effects via configurable models
- Enables testing without SDR hardware
- Supports multiple UEs with multiple simulator instances

### How It Works

1. **gNB** starts with `--rfsim` flag, acting as an RFSIM server
2. **nrUE** starts with `--rfsim` flag and `--rfsimulator.[0].serveraddr <gnb-ip>`, acting as RFSIM client
3. Both connect via **TCP port 4043**
4. The RFSIM channel simulator can apply:
   - Propagation delay
   - Noise
   - Fading models
   - Packet dropping

### Container Startup Sequence

```
mysql → oai-amf → oai-smf → oai-upf → oai-ext-dn
                                        ↓
                                     oai-gnb
                                        ↓
                                     oai-nr-ue
```

Each component depends on the previous ones being healthy.

---

## Common Commands Reference

### Container Management

```bash
# Start everything
sudo docker compose up -d

# Stop everything
sudo docker compose down

# Restart a specific container
sudo docker compose restart oai-gnb

# View logs (follow mode)
sudo docker logs -f rfsim5g-oai-gnb
sudo docker logs -f rfsim5g-oai-nr-ue
```

### Debugging

```bash
# Check if nrUE process is running
sudo docker exec rfsim5g-oai-nr-ue pgrep nr-uesoftmodem

# Check gNB process
sudo docker exec rfsim5g-oai-gnb pgrep nr-softmodem

# View full nrUE logs
sudo docker logs rfsim5g-oai-nr-ue 2>&1 | tail -100

# View full gNB logs
sudo docker logs rfsim5g-oai-gnb 2>&1 | tail -50

# View AMF logs for registration events
sudo docker logs rfsim5g-oai-amf 2>&1 | grep -i "register\|reject\|fail"

# Check all container health
sudo docker compose ps

# View all logs combined
sudo docker compose logs
```

### Network Inspection

```bash
# Enter nrUE container shell
sudo docker exec -it rfsim5g-oai-nr-ue /bin/bash

# Check UE tunnel interface inside container
sudo docker exec rfsim5g-oai-nr-ue ifconfig -a

# View routing from UE
sudo docker exec rfsim5g-oai-nr-ue route -n

# Check public network interfaces on host
ip addr

# Check docker networks
sudo docker network ls
sudo docker network inspect rfsim5g-public
```

---

## Troubleshooting

### Containers Not Starting

**Problem**: Containers fail to start or show `unhealthy` status.

**Solution**:
```bash
sudo docker compose down
sudo docker compose up -d
sleep 30
sudo docker compose ps
```

### "No such device" - oaitun_ue1

**Problem**: `ping: SO_BINDTODEVICE oaitun_ue1: No such device`

**Cause**: The tunnel interface hasn't been created yet. The nrUE software creates `oaitun_ue1` only after successful network registration.

**Solution**:
1. Check nrUE logs for registration status:
   ```bash
   sudo docker logs rfsim5g-oai-nr-ue 2>&1 | tail -100
   ```

2. Look for `NR_RRC_CONNECTED` in logs

3. If not connected, check:
   - gNB is running: `sudo docker logs rfsim5g-oai-gnb | grep RFSIM`
   - AMF acceptance: `sudo docker logs rfsim5g-oai-amf | grep -i accept`

### UE Not Connecting / Registration Failures

**Problem**: nrUE fails to reach `NR_RRC_CONNECTED` state.

**Checks**:
1. Verify gNB is running:
   ```bash
   sudo docker logs rfsim5g-oai-gnb | grep RFSIM
   ```

2. Check for errors in gNB:
   ```bash
   sudo docker logs rfsim5g-oai-gnb | grep -i error
   ```

3. Check AMF logs for registration rejection:
   ```bash
   sudo docker logs rfsim5g-oai-amf | grep -i reject
   ```

4. Verify network connectivity:
   ```bash
   sudo docker exec rfsim5g-oai-nr-ue ping -c 3 192.168.71.132
   ```

### Ping Fails (Even After Tunnel Appears)

**Problem**: Ping returns `100% packet loss` or `No such device`.

**Solution**:
```bash
# Try pinging by IP first (without -I flag)
sudo docker exec rfsim5g-oai-nr-ue ping 192.168.72.135

# Check if tunnel exists
sudo docker exec rfsim5g-oai-nr-ue ifconfig -a | grep tun

# From inside the container, try:
sudo docker exec rfsim5g-oai-nr-ue /bin/bash -c "ping -I oaitun_ue1 192.168.72.135"
```

### Port Conflicts

**Problem**: TCP port 4043 already in use.

**Solution**:
```bash
# Find what's using port 4043
sudo lsof -i :4043

# Kill if needed
sudo kill <pid>
```

### Docker Permission Denied

**Problem**: `permission denied while trying to connect to Docker daemon`

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes (logout and login, or:)
newgrp docker

# Or just use sudo for all docker commands
```

---

## Cleanup

### Stop All Containers

```bash
cd ~/openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator
sudo docker compose down
```

### Remove All Data (Optional)

```bash
# Remove containers and volumes (deletes UE state, databases)
sudo docker compose down -v
```

### Remove Docker Images (Optional)

```bash
sudo docker rmi $(sudo docker images | grep oaisoftwarealliance | awk '{print $3}')
```

---

## Alternative Emulated Modes

OAI supports three emulated modes:

| Mode | Command | Multi-UE | Description |
|------|---------|----------|-------------|
| **RF Emulator** | `nr-softmodem --device.name rf_emulator --phy-test` | No | Drops TX, generates noise RX |
| **RF Simulator** | Docker RFSIM containers | Yes | Simulates RF channel via TCP |
| **L2 nFAPI** | External proxy + nFAPI | Yes | Bypasses PHY entirely |

For **L2 nFAPI mode**, see: [oai-lte-multi-ue-proxy](https://github.com/EpiSci/oai-lte-multi-ue-proxy)

---

## Jetson Orin Nano Specific Notes

### ARM64 Architecture

The Jetson Orin Nano uses ARM64 architecture. The OAI Docker images (`oaisoftwarealliance/*`) are **x86_64 only**. For ARM64, you have two options:

1. **Use multi-arch images** if available
2. **Build your own Docker images** for ARM64
3. **Use QEMU emulation** (slower performance)

### Performance Considerations

- 8GB RAM Jetson: May need to reduce number of UE containers
- Use `docker stats` to monitor resource usage:
  ```bash
  sudo docker stats
  ```

### Checking Architecture

```bash
uname -m
# Should show: aarch64 on Jetson Orin Nano
```

---

## Further Reading

- [Official OAI NR SA Tutorial](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/NR_SA_Tutorial_OAI_nrUE.md)
- [OAI Documentation](../openairinterface/index.md)
- [Baseline Setup](../openairinterface/setup.md)
- [L2 Emulator Architecture](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/episys/nsa_mode_l2_emulator/README.md)

---

## Quick Reference

```bash
# Full startup sequence
cd ~/openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator
sudo docker compose up -d mysql oai-amf oai-smf oai-upf oai-ext-dn
sleep 20 && sudo docker compose up -d oai-gnb
sleep 10 && sudo docker compose up -d oai-nr-ue

# Verify UE registered (look for oaitun_ue1)
sudo docker exec rfsim5g-oai-nr-ue ifconfig -a | grep tun

# Ping test (only works after tunnel appears)
sudo docker exec rfsim5g-oai-nr-ue ping -I oaitun_ue1 -c 3 192.168.72.135

# Cleanup
sudo docker compose down
```
