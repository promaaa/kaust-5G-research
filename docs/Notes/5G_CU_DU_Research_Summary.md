# KAUST 5G Research: OAI CU/DU Separation with USRP B210

## Project Overview

**Goal:** Implement a 5G NR testbed with CU/DU separation for drone-based aerial networks. The vision is to have a drone carrying a DU + USRP B210 in the sky, connected via wireless 5G backhaul to a ground station with CN + CU.

## Machines Involved

| Machine | IP Addresses | Role | Status |
|---------|-------------|------|--------|
| **serber-firecell** | 10.76.170.45 (university eth), 10.0.0.1 (direct eth removed) | Core Network + CU (AMF) | ✅ Working |
| **serber-minipc** | 10.85.168.144 (WiFi), 10.0.0.2 (direct eth) | DU candidate | ⚠️ WiFi only |
| **serber-pi** | 10.76.170.117 (eth), 10.85.42.8 (WiFi iCampus) | DU (new) | ✅ Working |
| **oai** | 10.76.170.90 | PWS testing, USRP validation | ✅ Working |

## Architecture Vision

```
┌─────────────────────────────────────────────────────────────┐
│                    DRONE (Airborne)                          │
│  ┌─────────┐      ┌──────────┐      ┌─────────────────────┐  │
│  │   DU    │──────│   USRP   │      │   5G Backhaul       │  │
│  │(nr-soft │      │   B210   │      │   (Future: 5G NR    │  │
│  │ modem)  │      │ (RF TX)  │      │    wireless link)   │  │
│  └─────────┘      └──────────┘      └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ F1 (Ethernet/IP)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 GROUND STATION                               │
│  ┌─────────┐      ┌──────────┐      ┌─────────────────────┐  │
│  │   CU    │──────│   CN     │      │                     │  │
│  │         │      │ (Docker) │      │                     │  │
│  └─────────┘      └──────────┘      └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### F1 Interface (CU↔DU)
- **Protocol:** F1AP over SCTP/IP (Ethernet)
- **Current test:** Ethernet Direct (10.0.0.0/24)
- **Firewall/NAT:** SCTP traffic on 10.0.0.1:38412 DNAT-forwarded to AMF container

## What Has Been Accomplished

### 1. Ethernet Direct CU/DU Connection ✅
- Successfully connected serber-firecell (10.0.0.1) and serber-minipc (10.0.0.2) via direct Ethernet
- Full SCTP handshake and gNB registration confirmed
- gNB ID: 0x0E00, PLMN: 208.95, Cell ID: 12345678
- AMF sees gNB as "Connected"

**Issue:** Direct Ethernet on minipc (enp4s0) is currently **DOWN** (NO-CARRIER) — physical connection needs verification.

### 2. serber-pi as DU (Raspberry Pi 5) ✅ (NEW)
- Successfully set up Raspberry Pi 5 (4GB) as DU
- Connected to iCampus WiFi (WPA-EAP/TTLS/MSCHAPV2)
- Built nr-softmodem from source for ARM64 (RFsim mode)
- AMF on serber-firecell now running with IP 10.76.170.45 (fixed from 10.0.0.1)
- **gNB (serber-pi) successfully connects to AMF via NGAP/SCTP**
- gNB ID: 0x0E00, PLMN: MCC=208, MNC=95, TAC: 0xa000
- AMF shows gNB as "Connected" status

**Key Fix:** Removed conflicting 10.0.0.1/24 IP from serber-firecell enp6s0 so AMF registers with 10.76.170.45

### 3. USRP B210 Validation ✅
- USRP B210 (serial: 35F8ABA) tested on **oai** machine (10.76.170.90)
- FPGA loaded successfully (v16.0)
- USB 3.0 connection verified
- TX/RX paths functional
- UHD version 4.8.0.HEAD installed

**TX Test Results:**
- Frequency: 2.5 GHz sine wave transmitted successfully
- UHD probe confirmed all frontend paths

### 4. gNB + Core Network on oai ✅
- Core Network running (docker containers: oai-amf, oai-smf, oai-upf, etc.)
- gNB (nr-softmodem) built and running
- UE registration working (1 UE registered: IMSI 001010000059453)
- Config: `gnb.sa.band78.fr1.106PRB.usrpb210.conf`
- **Fixed:** Serial was incorrectly set to `8002816`, changed to `35F8ABA`

### 5. PWS/SIB8 Warning System ✅
- SIB8 configured with message: "Hello this is a warning message."
- Message ID: 1112, Serial: FF44
- NMS backend running on port 3001
- NMS frontend running on port 5173 (after Node.js upgrade to v20)

### 6. UHD Installation on serber-firecell ✅
- UHD 4.9.0 installed via PPA
- FPGA images downloaded to `/usr/share/uhd/4.9.0/images/`
- USRP B210 detected successfully (serial: 35F8ABA)

## Current Issues

### Issue 1: Direct Ethernet on serber-minipc is DOWN (Resolved for serber-pi)
```
enp4s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> state DOWN
Link detected: no
```
**Cause:** Physical link not established
**Fix:** Using serber-pi as new DU instead; serber-minipc remains for backup

### Issue 2: USRP B210 Location
- USRP B210 is physically connected to **serber-firecell**
- UHD was originally installed on **serber-minipc**
- Decision: Keep USRP on firecell (main rig) since it works there

### Issue 3: DU Binary Not on firecell
- OAI DU (nr-softmodem) built on serber-minipc
- serber-firecell has no DU binary
- Options: Build OAI on firecell OR move USRP to minipc

### Issue 4: AMF Network Configuration (RESOLVED)
- AMF was registering with 10.0.0.1 instead of 10.76.170.45
- **Fix Applied:** Removed 10.0.0.1/24 from serber-firecell enp6s0
- AMF now correctly registers with 10.76.170.45

### Issue 5: WiFi Connection (RESOLVED)
- iCampus WiFi uses WPA-EAP (TTLS/MSCHAPV2)
- PEAP authentication method works
- WiFi provides connectivity but CN subnet unreachable - use Ethernet for CN

## Planned Next Steps

### Phase 1: USRP B210 Integration with CU/DU (Current)
1. **serber-pi is now working as DU** - connected to AMF successfully
2. **Next:** Test with USRP B210 hardware connected to serber-pi
3. **Build or copy DU binary** to serber-firecell (for USRP testing)
4. **Create gnb-usrp-b210.conf** for firecell
5. **Test full CU/DU + USRP** on firecell

### Phase 2: 5G Backhaul Research
**Vision:** Use 5G NR as wireless backhaul between DU (drone) and CU (ground)

**Requirements:**
- 2x USRP B210 units (one for each side)
- DU + USRP on drone
- CU + CN + USRP on ground
- Point-to-point 5G NR link for F1 traffic

**Challenge:** USB cables cannot reach from ground to drone
- **Solution 1:** Both USRP + DU co-located on drone (same machine)
- **Solution 2:** Use Ethernet-based radio heads (E310, commercial O-RAN RU)

### Phase 3: Drone Integration
- Mount DU + USRP on drone
- Establish 5G backhaul to ground station
- Test real flight scenarios

## Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `gnb-sa.band78.rfsim.conf` | ~/oai-du/ (serber-pi) | Working RFsim config for DU |
| `gnb-ethernet-direct.conf` | ~/oai-du/ | Working rfsim config for Ethernet direct |
| `gnb-usrp-b210.conf` | ~/oai-du/ | USRP B210 config (created by AI) |
| `gnb.sa.band78.fr1.106PRB.usrpb210.conf` | ~/sib8-spoofing/targets/PROJECTS/GENERIC-NR-5GC/CONF/ | PWS test config |
| `sib8.conf` | ~/sib8-spoofing/ | PWS warning message |
| `basic_nrf_config.yaml` | ~/oai-cn/docker-compose/conf/ | AMF/SMF/UDR/UDM/AUSF/NRF config |

## serber-pi (DU) Setup Details

### SSH Access
```bash
sshpass -p 'root4SERBER' ssh -o StrictHostKeyChecking=no serber@10.76.170.117
```

### Build Libraries (if rebuilding)
```bash
cd ~/openairinterface5g/cmake_targets/ran_build/build
make params_libconfig    # For libparams_libconfig.so
make rfsimulator         # For librfsimulator.so
```

### Run DU (RFsim mode)
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/openairinterface5g/cmake_targets/ran_build/build
cd ~/oai-du
sudo ./nr-softmodem -O gnb-sa.band78.rfsim.conf --rfsim --thread-pool 1 -g 2
```

### Check SCTP Association
```bash
cat /proc/net/sctp/assocs
```

### Check AMF gNB Status (on serber-firecell)
```bash
sudo docker logs oai-amf --tail 30 | grep gNB
```

## SSH Credentials

| Machine | Username | Password |
|---------|----------|----------|
| serber-firecell | serber | root4SERBER |
| serber-minipc | serber | root4SERBER |
| serber-pi | serber | root4SERBER |
| oai | oai | root4SERBER |

## Important Commands

### Check USRP Detection
```bash
uhd_find_devices
uhd_usrp_probe --args 'serial=35F8ABA'
```

### Check AMF NAT Rules (firecell)
```bash
sudo iptables -t nat -L PREROUTING -n | grep 38412
```

### Check AMF Container IP
```bash
sudo docker inspect oai-amf | grep '"IPAddress"'
```

### Check serber-firecell enp6s0 IP (should NOT have 10.0.0.1)
```bash
ip addr show enp6s0
# If 10.0.0.1 exists, remove it:
sudo ip addr del 10.0.0.1/24 dev enp6s0
```

### Restart AMF after network changes
```bash
sudo docker restart oai-amf
# Check logs:
sudo docker logs oai-amf --tail 30
```

### Start gNB
```bash
cd ~/sib8-spoofing/cmake_targets/ran_build/build
sudo ./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf -E --continuous-tx
```

## Research Reports

- `Research Progress Report 3.md` — Previous report
- `Research Progress Report 4.md` — Ethernet Direct success, USRP testing

## Notes

- **serber-pi as DU:** Successfully replaces serber-minipc as DU candidate
- **serber-minipc:** Remains available as backup, currently on WiFi only
- **WiFi was temporary:** iCampus WiFi (PEAP auth) used only for remote access — should not appear in research reports
- **USRP B210 power:** Requires external power adapter, USB 3.0 cable (not power-only)
- **CU/DU split in OAI:** F1 interface runs over Ethernet/IP, not USB
- **UHD limitation:** UHD driver must run locally with USRP — no network remote control
- **serber-firecell networking:** AMF binds to enp6s0 (10.76.170.45). The 10.0.0.1 IP was removed to prevent AMF registration issues
- **Docker AMF:** oai-amf container runs with --network host, binds to host's network namespace
