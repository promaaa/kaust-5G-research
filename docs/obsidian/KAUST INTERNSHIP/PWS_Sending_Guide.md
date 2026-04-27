# OAI Public Warning System (PWS) — Complete Setup Guide

## Overview

This document explains how to send emergency broadcast messages (PWS/SIB8) using OpenAirInterface. The system works by placing a `sib8.conf` configuration file in the OAI working directory — a 5-second timer watches for changes and automatically rebuilds and retransmits the SIB8 warning message over the air.

A Nothing Phone (5G UE) is connected to the network and will receive the broadcast when the gNB is running.

---

## Architecture

```
serber-pi (10.85.42.8)          serber-firecell (10.76.170.45)
+--------------------+           +------------------------+
| DU + USRP B210    |---NGAP---->| AMF + CN (Docker)     |
| nr-softmodem      |---SCTP---->| 172.18.0.9            |
| PWS (sib8.conf)   |           +------------------------+
+--------------------+
         |
         | F1 (SCTP)
         ▼
   Nothing Phone (UE)
```

---

## Method 1: Using the NMS Web Interface

The Network Management System (NMS) provides a web UI for live configuration of SIB8 parameters without restarting the gNB.

### Prerequisites

- OAI PC at `10.76.170.90` with:
  - Core Network (docker containers) running
  - NMS backend running on port 3001
  - NMS frontend accessible at port 5173
  - nr-softmodem running with the PWS patch applied

### Steps

**1. Start the Core Network:**
```bash
sshpass -p 'root4SERBER' ssh serber@10.76.170.45
cd ~/oai-cn5g/
docker compose up -d
```

**2. Start the NMS backend:**
```bash
cd ~/5g-sib8-alert/assets/
./start-nms.sh
```

**3. Open the web interface:**
```
http://10.76.170.90:5173
```

**4. Modify SIB8 parameters:**
- Message ID: `1112` (Presidential), `1113` (Extreme), `1115` (Severe)
- Serial Number: `3FF1` — **change this to force re-display on Samsung UEs**
- Data Coding Scheme: `48` (UCS-2) or `01` (GSM-7)
- Text: Your alert message (use `|` for newlines)
- Mode: `0` (multi-segment)

**5. Click Save — the change is written to `~/openairinterface5g/sib8.conf`**

**6. The 5-second PWS timer detects the file change and retransmits the SIB8**

---

## Method 2: Manual sib8.conf Editing

### Step 1: Locate the correct sib8.conf

When running from `~/openairinterface5g/cmake_targets/ran_build/build/`, the resolved path is:
```
~/openairinterface5g/sib8.conf
```

### Step 2: Edit sib8.conf

```bash
sshpass -p 'root4SERBER' ssh serber@10.85.42.8
nano ~/openairinterface5g/sib8.conf
```

Example:
```
messageIdentifier=1112;
serialNumber=0000;
dataCodingScheme=48;
text=This is a test emergency alert.|Second line here.;
mode=0;
```

### Step 3: Start the gNB

```bash
cd ~/openairinterface5g/cmake_targets/ran_build/build
sudo ./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf -E --continuous-tx
```

- `-E --continuous-tx` — Continuous transmission (required for real RF)
- `-O <config>` — Path to gNB configuration file

### Step 4: Trigger Alert

Every file save of `sib8.conf` triggers the 5-second timer to broadcast. To force an immediate retransmit:
```bash
touch ~/openairinterface5g/sib8.conf
```

---

## sib8.conf Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `messageIdentifier` | `1112` (Presidential), `1113` (Extreme), `1115` (Severe) | 3GPP alert type |
| `serialNumber` | Hex e.g. `3FF1`, `0000`, `0001` | Change to re-display on Samsung UEs (they cache this) |
| `dataCodingScheme` | `01` (GSM-7, 93 chars/seg), `48` (UCS-2, 82 bytes/seg) | Encoding |
| `text` | Any string | Alert content. Use `\|` for newlines |
| `mode` | `0`, `1`, `2` | `0` = multi-segment |

---

## Complete Startup Sequence

```bash
# 1. Core Network
sshpass -p 'root4SERBER' ssh serber@10.76.170.45
cd ~/oai-cn5g/
docker compose up -d
sleep 10

# 2. gNB with USRP B210 + PWS
sshpass -p 'root4SERBER' ssh serber@10.85.42.8
cd ~/openairinterface5g/cmake_targets/ran_build/build
sudo ./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf -E --continuous-tx

# 3. Edit sib8.conf to trigger alert
nano ~/openairinterface5g/sib8.conf
```

---

## PWS Code Flow

```
Timer (5s periodic)
    │
    └─► handle_pws_timer_expiry()         [rrc_gNB.c]
            │
            │  (checks: did sib8.conf mtime/size change?)
            │
            └─► write_replace_warning_req_trigger()  [rrc_gNB_du.c]
                    │
                    ├─ build_sib8_segments()      [asn1_msg.c]
                    │      ├─ reads sib8.conf
                    │      ├─ GSM-7 or UCS-2 encoding
                    │      └─ ASN.1 encode as NR_SIB8_t
                    │
                    └─► rrc->mac_rrc.write_replace_warning_req()
                              │
                              └─► write_replace_warning_req()  [mac_rrc_dl_handler.c]
                                      │
                                      └─► nr_mac_configure_pws_si()  [config.c]
                                              │
                                              └─► schedule_nr_other_sib() → OTA TX
```

**Log grep targets:**
```bash
grep -E "SIB8|write_replace_warning|pws_timer|sib8.conf" nr-softmodem.log
```

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| UE doesn't show alert | Samsung cached serial number | Change `serialNumber` to new value |
| UE doesn't show alert | No UE connected | Ensure UE is registered on the network |
| No PWS activity in logs | Timer not initialized | Check gNB built with PWS patch |
| "mac_rrc.write_replace_warning_req not initialized" | Patch not applied | Rebuild with `git apply oai-alert.patch` |
| "cannot decode SIB8 from CU" | Wrong SIB8 encoding | Verify `dataCodingScheme` matches encoding |

---

## Key Files

| File | Path |
|------|------|
| sib8.conf | `~/openairinterface5g/sib8.conf` |
| gNB config | `~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf` |
| PWS patch | Applied via `oai-alert.patch` |
| nr-softmodem | `~/openairinterface5g/cmake_targets/ran_build/build/nr-softmodem` |
| Core Network | `~/oai-cn5g/` (docker compose) |
