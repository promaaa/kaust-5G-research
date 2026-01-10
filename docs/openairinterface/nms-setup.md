# OpenAirInterface – NMS and SIB8 Setup

This document describes how a **baseline OpenAirInterface (OAI) 5G Standalone deployment** is extended to support **SIB8 emergency alert transmission** and a custom **Network Management System (NMS)**.

> **NOTE:**
> The baseline OAI setup described in [`setup.md`](setup.md) **must be completed first**.

## Overview

This repository contains the NMS code and a patch file that extend the OAI project to support SIB8 emergency alert transmission.

The implementation is based on OpenAirInterface commit: `92980ceb725a94dbfe97c509d16f1313eee083e0`

The provided patch implements:
- Construction of SIB8 warning messages in the RRC layer
- Support for segmented SIB8 transmission using multiple System Information messages
- Support for multiple data coding scheme (GSM 7-bit and UCS2)

The NMS allows users to:
- Modify SIB8 warning message parameters
- Configure key gNB parameters (e.g. PLMN, cell identity..)
- Manage basic subscriber data in the core network

## Tutorial

### Core Network

Clone the current repository:
```bash
git clone https://github.com/5gattacks/internship-docs.git ~/5g-sib8-alert
```

Replace OAI CN docker compose file:
```bash
cp ~/5g-sib8-alert/assets/configuration/oai-docker-compose.yml ~/oai-cn5g/docker-compose.yaml
```

### gNB

Build gNB:
```
cd ~/openairinterface5g
git checkout 92980ceb725a94dbfe97c509d16f1313eee083e0
git apply ~/5g-sib8-alert/assets/oai-alert.patch

# Build OAI gNB
cd ~/openairinterface5g/cmake_targets
sudo ./build_oai -w USRP --ninja --gNB -C
```

### Run NMS and OAI

#### CN

Start:
```bash
cd ~/oai-cn5g/
docker compose up -d
```

Stop:
```bash
cd ~/oai-cn5g/
docker compose down
```

#### NMS

Start:
```bash
cd ~/5g-sib8-alert/assets/
./start-nms.sh
```
The web interface is accessible at http://localhost:3000/.

Stop:
```bash
cd ~/5g-sib8-alert/assets/
./stop-nms.sh
```
**NOTE:** You should configure the parameters before running the gNB.

#### gNB:

Start:
```bash
cd ~/openairinterface5g/cmake_targets/ran_build/build
sudo ./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf -E --continuous-tx
```
Press `Ctrl+C` to stop the gNB.

