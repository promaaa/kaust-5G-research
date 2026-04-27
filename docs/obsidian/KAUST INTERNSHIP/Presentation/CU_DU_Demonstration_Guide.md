# CU/DU Split Demonstration Guide

A step-by-step guide to perform a full 5G NR CU/DU split demonstration using **Raspberry Pi 5** as DU and **serber-firecell** as CU + Core Network.

---

## Overview

This guide walks you through setting up and running a complete CU/DU split architecture with:

- **DU (Distributed Unit):** Raspberry Pi 5 running OAI nr-softmodem
- **CU + CN (Central Unit + Core Network):** serber-firecell running OAI containers

```
┌─────────────────────┐         ┌─────────────────────────────────┐
│    serber-pi        │         │       serber-firecell            │
│   (Raspberry Pi 5)  │   F1    │         (Core Machine)          │
│                     │◄────────┼────────────────────────────────►│
│  ┌───────────────┐  │  SCTP   │  ┌───────┐  ┌──────┐  ┌──────┐ │
│  │  DU (L1+MAC)  │  │         │  │  CU   │──│ AMF  │──│ SMF  │ │
│  │ nr-softmodem  │  │         │  │       │  │      │  │      │ │
│  └───────────────┘  │         │  └───────┘  └──────┘  └──────┘ │
│                     │         │                          ┌──────┐ │
│  IP: 10.85.42.8     │         │  IP: 10.76.170.45       │ UPF  │ │
└─────────────────────┘         │                          └──────┘ │
                               └─────────────────────────────────┘
```

---

## Prerequisites

Before starting, ensure you have:

- Access to both machines via SSH
- USRP B210 connected to serber-firecell (optional for rfsim mode)
- Core Network containers running on serber-firecell

---

## Step 1: Verify Core Network is Running

On **serber-firecell**, check that all OAI containers are healthy:

```bash
sudo docker ps --format "table {{.Names}}\t{{.Status}}"
```

You should see these containers running:
- `oai-amf`
- `oai-smf`
- `oai-upf`
- `oai-nrf` (optional)
- `mysql` (for database)

### If containers are not running:

```bash
cd ~/oai-cn/docker-compose
sudo docker-compose up -d
sudo docker logs oai-amf --tail 20
```

---

## Step 2: Check AMF is Listening

On **serber-firecell**, verify the AMF SCTP endpoint is listening:

```bash
sudo lsof -i :38412
```

Expected output shows SCTP listener on port 38412.

### If AMF is not listening:

```bash
sudo docker restart oai-amf
sleep 5
sudo lsof -i :38412
```

---

## Step 3: Connect to serber-pi (Raspberry Pi 5)

From your local machine:

```bash
sshpass -p 'root4SERBER' ssh -o StrictHostKeyChecking=no serber@10.76.170.117
```

### Verify network connectivity to serber-firecell:

```bash
ping -c 3 10.76.170.45
```

---

## Step 4: Prepare the DU Configuration

On **serber-pi**, create or verify the 24 PRB configuration file:

```bash
nano ~/gnb-du.sa.band78.24prb.usrpb210.conf
```

Paste this configuration:

```
Active_gNBs =
(
    {
        .gNB_ID = 0x0E00,
        .name = "gNB-Pi5-24PRB-DU",
        .cell_type = MACRO_GNB,

        .pdcch_Carrier = {
            .pdcch_DMRS_ScramblingID = 0,
            .pdcch_StartSymbol = 2,
            .pdcch_OffsetFirstCarrie = 0,
        },

        .pdsch_Config = {
            .pdsch_PRB_BundlingType = "bundling",
            .pdsch_PRB_BundlingSize = 1,
            .pdsch_RV_Index = 0,
        },

        .num_CC = 1,

        .plmn_list = ({
            .mcc = 208,
            .mnc = 95,
            .mnc_length = 2,
        }),

        .tracking_area_code = 0xa000,
        .qos_profile = ({
            .fiveQI = 9,
            .priority_level = 1,
        }),

        .f1ing_f1ap_ip_addr = "10.85.42.8",
        .F1_CU_IP_address = "10.76.170.45",
        .F1_CU_port = 38412,
    }
);

THREAD_PARAMS = (
    {
        .thread_map = 0x000000000000000F,
        .UL_num_threads = 1,
        .DL_num_threads = 1,
    }
);

USRP_Params =
(
    {
        master_clock = 30.72e6,
        sdr_addrs = "type=b200,serial=35F8ABA",
    }
);

macro_gNB_CellGroup =
(
    {
        .num_cells = 1,

        .primary_cell = {
            .cell_id = 12345678,
            .pCI = 0,
            .eUTRA_band_number = 78,
            .dl_frequency = 3604800000,
            .ul_frequency_offset = -180000000,
            .N_RB_DL = 24,
            .N_RB_UL = 24,
            .N_DL_RB = 24,
            .frame_duplex_type = FDD,
            .Fdd_Dl_Scenario = {
                .sc_Scenario = 0,
            },
            .initialDLBWP = {
                .initialDLBWPcontrolResourceSetZero = 2,
                .initialDLBWPsearchSpaceZero = 0,
            },
            .initialULBWP = {
                .initialULBWPcontrolResourceSetZero = 0,
                .initialULBWPsearchSpaceZero = 0,
            },
        },

        .Nid_cell = 0,
        .nARFCN_DL = 640320,
        .nARFCN_UL = 640320,
        .frame_type = FDD,
        .tdd_Config = {
            .initialDownlinkBWP = 0,
            .initialUplinkBWP = 0,
        },
        .dl_Sl_Category = 0,
        .ul_Sl_Category = 0,
    }
);

NETWORK_INTERFACES :
{
    GNB_IPV4_ADDRESS_FOR_NG_AMF = "10.85.42.8";
    GNB_IPV4_ADDRESS_FOR_F1 = "10.85.42.8";
    GNB_PORT_FOR_NG_AMF = 38412;
    GNB_PORT_FOR_F1 = 38412;
};
```

---

## Step 5: Build or Verify DU Binary

On **serber-pi**, check if nr-softmodem exists:

```bash
ls -la ~/oai-du/nr-softmodem
```

### If binary does not exist, build it:

```bash
cd ~/openairinterface5g/cmake_targets/ran_build/build
make -j$(nproc) nr-softmodem
```

### Verify libraries are available:

```bash
ls -la ~/openairinterface5g/cmake_targets/ran_build/build/*.so
```

---

## Step 6: Start the DU (nr-softmodem)

On **serber-pi**, set up the environment and start the DU:

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/openairinterface5g/cmake_targets/ran_build/build
cd ~/oai-du

sudo ./nr-softmodem -O gnb-du.sa.band78.24prb.usrpb210.conf --rfsim --thread-pool 1 -g 2
```

### Expected output:

```
[GNB_APP] F1AP: gNB idx 0 gNB_DU_id 1, gNB_DU_name gNB-Pi5-24PRB-DU
[GNB_APP] Configured DU: cell ID 12345678, PCI 0
[F1AP] Starting F1AP at DU
[F1AP] F1-C DU IPaddr 10.85.42.8, connect to F1-C CU 10.76.170.45
```

Keep this terminal open.

---

## Step 7: Verify F1-C Connection on serber-firecell

Open a new SSH session to **serber-firecell**:

```bash
sshpass -p 'root4SERBER' ssh -o StrictHostKeyChecking=no serber@10.76.170.45
```

### Check SCTP association:

```bash
cat /proc/net/sctp/assocs
```

You should see an association with state ESTABLISHED.

### Check AMF logs for gNB connection:

```bash
sudo docker logs oai-amf --tail 50 | grep -E "gNB|F1AP|F1-C"
```

Expected messages:
```
[gNB] gNB_id 0x0E00 connected to AMF
[F1AP] F1-C connection established from 10.85.42.8
```

---

## Step 8: Verify CU is Functioning

On **serber-firecell**, check that the CU (gNB application) is running:

```bash
sudo docker ps | grep oai
```

### Check the CU process inside the container:

```bash
sudo docker exec -it oai-amf bash -c "ps aux | grep nr-softmodem"
```

If no CU process is found, you may need to start the CU separately or it may be co-located with AMF in your setup.

---

## Step 9: Connect a UE (Optional)

If you have a 5G UE (phone or simulator), configure it to connect:

| Setting | Value |
|---------|-------|
| MCC/MNC | 208/95 |
| TAC | 0xa000 (40960) |
| gNB ID | 0x0E00 (3584) |
| Cell ID | 12345678 |

The UE should search for the DU at 10.85.42.8 and register through the AMF.

---

## Step 10: Monitor and Troubleshoot

### DU side (serber-pi):

```bash
# Check CPU usage
top -bn1 | grep nr-softmodem

# Check SCTP connections
cat /proc/net/sctp/assocs

# View DU logs (in another terminal)
tail -f /tmp/nr-softmodem.log
```

### CU/CN side (serber-firecell):

```bash
# Check AMF logs
sudo docker logs oai-amf --tail 100 -f

# Check SMF logs
sudo docker logs oai-smf --tail 50

# Check UPF logs
sudo docker logs oai-upf --tail 50

# Check for SCTP errors
sudo docker logs oai-amf 2>&1 | grep -i "sctp\|error"
```

---

## Troubleshooting

### Issue: DU fails to start with F1-C error

**Cause:** Network connectivity issue between serber-pi and serber-firecell

**Solution:**
```bash
# On serber-pi, test connectivity
ping 10.76.170.45

# On serber-firecell, check firewall
sudo iptables -L -n | grep 38412

# If firewall blocks, add rule:
sudo iptables -A INPUT -p sctp --dport 38412 -j ACCEPT
```

### Issue: AMF not listening on port 38412

**Solution:**
```bash
# Restart AMF container
sudo docker restart oai-amf
sleep 10
sudo lsof -i :38412
```

### Issue: SCTP association fails to establish

**Cause:** Security modules (IPsec/SCTP) may be blocked

**Solution:**
```bash
# On serber-firecell
sudo modprobe sctp
sudo sysctl -w net.sctp.cache_enable=1
```

---

## Stopping the Demonstration

### 1. Stop DU (on serber-pi):
Press `Ctrl+C` in the terminal running nr-softmodem.

### 2. Stop Core Network (on serber-firecell):
```bash
sudo docker-compose down
```

---

## Quick Reference Card

| Action | Machine | Command |
|--------|---------|---------|
| SSH to DU | Local | `sshpass -p 'root4SERBER' ssh serber@10.76.170.117` |
| SSH to CU/CN | Local | `sshpass -p 'root4SERBER' ssh serber@10.76.170.45` |
| Start DU | serber-pi | `sudo ./nr-softmodem -O gnb-du.sa.band78.24prb.usrpb210.conf --rfsim` |
| Check AMF | serber-firecell | `sudo docker logs oai-amf --tail 30` |
| Check SCTP | serber-firecell | `cat /proc/net/sctp/assocs` |
| Stop DU | serber-pi | `Ctrl+C` |

---

## Network Summary

| Component | IP Address | Port | Notes |
|-----------|------------|------|-------|
| DU (serber-pi) | 10.85.42.8 | 38412 | F1-C endpoint |
| CU (serber-firecell) | 10.76.170.45 | 38412 | F1-C + N2 endpoint |
| AMF | 10.76.170.45 | 38412 | NGAP termination |
| SMF | 10.76.170.45 | 8800 | PFCP endpoint |
| UPF | 10.76.170.45 | 2152 | GTP-U endpoint |

---

## Configuration Files Location

| File | Location | Purpose |
|------|----------|---------|
| DU config | `~/oai-du/gnb-du.sa.band78.24prb.usrpb210.conf` | 24 PRB, band n78 |
| AMF config | `~/oai-cn/docker-compose/conf/*.yaml` | Core network |
| CN configs | `~/oai-cn/docker-compose/` | docker-compose |

---

**Good luck with your demonstration!**