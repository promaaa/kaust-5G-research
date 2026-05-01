# Research Progress Report 6: Nothing Phone UE Integration & PWS Capability

**Date:** April 30, 2026
**Author:** Research Team
**Timeline:** April 7 – July 31, 2025 (16 weeks)

---

## Executive Summary

This report documents the successful integration of a Nothing Phone as a User Equipment (UE) connected to our 5G network infrastructure. We successfully established a working 5G connection with Public Warning System (PWS) capability on the serber-firecell machine. The UE can now register to the network, and we are working on stabilizing the PDU session for data connectivity and speed testing.

---

## 1. Network Architecture

### 1.1 Infrastructure Overview

| Component | Machine | IP Address | Role |
|-----------|---------|------------|------|
| Core Network (5GC) | serber-firecell | 192.168.70.132 | AMF, SMF, NRF, UPF |
| Radio Access Network (gNB) | serber-firecell | 192.168.70.129 | 5G Base Station |
| User Equipment (UE) | Nothing Phone | N/A | Smartphone |

### 1.2 Network Configuration

| Parameter | Value |
|-----------|-------|
| PLMN | 001/01 |
| Frequency Band | 78 (n78, 3300-3800 MHz) |
| PRB Configuration | 106 PRB (40 MHz) |
| Subcarrier Spacing | 30 kHz (Numerology 1) |
| AMF IP | 192.168.70.132 |
| gNB IP | 192.168.70.129 |

---

## 2. Repository Setup

### 2.1 OpenAirInterface 5G Repository

The main RAN repository is located at `~/openairinterface5g/` on serber-firecell.

**Applied Patch:** `oai-warning.patch`
- This patch enables PWS (Public Warning System) functionality
- Modified commit: `102965a669`
- Required `git reset --hard` before applying due to prior modifications

### 2.2 5G Core Network Docker Compose

Located at `~/oai-cn5g/`, this contains the containerized core network components.

**Key Containers:**
- `oai-amf` - Access and Mobility Management Function
- `oai-smf` - Session Management Function
- `oai-nrf` - Network Repository Function
- `oai-upf` - User Plane Function

---

## 3. UE Configuration (Nothing Phone)

### 3.1 SIM Card Details

The Nothing Phone uses a custom SIM with the following parameters:

| Parameter | Value |
|-----------|-------|
| IMSI | 001010000059449 |
| Authentication | 5G_AKA with Milenage algorithm |
| Ki | 5686e601f3a1942d4c5cd262ba6b4b20 |
| OPc | aeb1cabd8ed7a09b48d17eb3d8af172c |

### 3.2 SIM Registration

The SIM was added to the database using the following steps:

```bash
# Connect to MySQL database
docker exec -it mysql mysql -u root -poai123

# Add the Nothing Phone SIM
USE oai_db;
INSERT INTO subscribers (imsi, pdu_session_id, opc, key, amf, sqn, m5g_confirmed) 
VALUES ('001010000059449', 0, 'aeb1cabd8ed7a09b48d17eb3d8af172c', '5686e601f3a1942d4c5cd262ba6b4b20', '8000', 0, 1);
```

### 3.3 Database Persistence

To ensure the SIM persists across container restarts, the `oai_db.sql` file was updated:

```bash
# Location: ~/oai-cn5g/database/oai_db.sql
```

After any database changes, restart the AMF container:
```bash
docker-compose -f ~/oai-cn5g/docker-compose.yaml restart oai-amf
```

---

## 4. SSH Access Commands

### 4.1 Connecting to serber-firecell

```bash
ssh root@192.168.70.132
# Password: root4SERBER
```

### 4.2 Connecting to serber-minipc (Reference Machine)

```bash
ssh root@10.76.170.45
# Password: root4SERBER
```

---

## 5. Complete Startup Procedure

Execute these commands in sequence on serber-firecell to start the 5G network:

### Step 1: Reset USRP USB (if not detected)

```bash
# Unbind USB device
echo "2-6" | sudo tee /sys/bus/usb/drivers/usb/unbind

# Wait 2 seconds
sleep 2

# Rebind USB device
echo "2-6" | sudo tee /sys/bus/usb/drivers/usb/bind

# Wait 3 seconds for device to be recognized
sleep 3

# Verify USRP is detected
uhd_find_devices
```

### Step 2: Start 5G Core Network

```bash
# Navigate to 5G core directory
cd ~/oai-cn5g

# Start core network containers
docker-compose up -d

# Verify all containers are running
docker ps
```

### Step 3: Verify AMF Registration with NRF

```bash
# Check SMF logs for successful NRF registration
docker logs oai-smf 2>&1 | grep -i "nrf\|register" | tail -5
```

### Step 4: Start gNB

```bash
# Navigate to RAN build directory
cd ~/openairinterface5g/cmake_targets/ran_build/build

# Start gNB with continuous transmission
sudo nohup ./nr-softmodem \
  -O ~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf \
  -E --continuous-tx > ~/gnb.log 2>&1 &

# Wait for gNB to initialize
sleep 5

# Verify gNB started successfully
tail -30 ~/gnb.log
```

### Step 5: Verify gNB Registration with AMF

```bash
# Check AMF logs for gNB registration
docker logs oai-amf 2>&1 | grep -i "gnb\|register" | tail -5
```

### Step 6: Connect UE (Nothing Phone)

1. Enable airplane mode on the Nothing Phone
2. Wait 2 seconds
3. Disable airplane mode
4. The phone should search for and connect to the 5G network

### Step 7: Verify UE Registration

```bash
# Check AMF for UE connection
docker logs oai-amf 2>&1 | grep "UEs" | tail -1

# Check for specific UE (IMSI)
docker logs oai-amf 2>&1 | grep "001010000059449" | tail -5
```

---

## 6. Configuration Files

### 6.1 gNB Configuration

**File:** `~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf`

Key parameters:
- Band: 78
- PRB: 106
- Numerology: 1 (30 kHz SCS)
- AMF IP: 192.168.70.132
- gNB IP: 192.168.70.129

### 6.2 SIB8/PWS Configuration

**File:** `~/openairinterface5g/sib8.conf`

This file configures the Public Warning System broadcast parameters.

---

## 7. Monitoring Commands

### 7.1 gNB Logs

```bash
# Real-time gNB log monitoring
tail -f ~/gnb.log

# Search for specific patterns
grep -i "error\|warning\|registered" ~/gnb.log | tail -20
```

### 7.2 AMF Logs

```bash
# View AMF container logs
docker logs oai-amf 2>&1 | tail -50

# Search for UE-related messages
docker logs oai-amf 2>&1 | grep -i "ue\|pdu\|session" | tail -20

# Check number of connected UEs
docker logs oai-amf 2>&1 | grep "UEs" | tail -1
```

### 7.3 SMF Logs

```bash
# View SMF container logs
docker logs oai-smf 2>&1 | tail -50

# Check PDU session status
docker logs oai-smf 2>&1 | grep -i "pdu\|session" | tail -20
```

### 7.4 USRP Status

```bash
# Check if USRP devices are detected
uhd_find_devices

# Check USRP firmware
uhd_usrp_info
```

---

## 8. Troubleshooting Guide

### 8.1 USRP Not Detected

**Symptom:** `uhd_find_devices` returns no devices

**Solution:**
```bash
echo "2-6" | sudo tee /sys/bus/usb/drivers/usb/unbind
sleep 2
echo "2-6" | sudo tee /sys/bus/usb/drivers/usb/bind
sleep 3
uhd_find_devices
```

### 8.2 AMF Container Unhealthy

**Symptom:** `docker ps` shows AMF as unhealthy

**Solution:**
```bash
cd ~/oai-cn5g
docker-compose restart oai-amf
docker logs oai-amf 2>&1 | tail -20
```

### 8.3 UE Not Registering

**Symptom:** UE shows "No Service" or cannot connect

**Troubleshooting:**
1. Check if gNB is running: `ps aux | grep nr-softmodem`
2. Verify AMF is healthy: `docker logs oai-amf 2>&1 | grep -i "unhealthy"`
3. Check SIM is in database: `docker exec -it mysql mysql -u root -poai123 -e "USE oai_db; SELECT * FROM subscribers WHERE imsi='001010000059449';"`
4. Verify USRP is detected: `uhd_find_devices`

### 8.4 gNB Crashes

**Symptom:** `nr-softmodem` process terminates unexpectedly

**Solution:**
```bash
# Check crash logs
tail -100 ~/gnb.log | grep -i "segfault\|signal\|crash"

# Restart gNB
pkill -9 nr-softmodem
cd ~/openairinterface5g/cmake_targets/ran_build/build
sudo nohup ./nr-softmodem -O ~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf -E --continuous-tx > ~/gnb.log 2>&1 &
```

### 8.5 PDU Session Failures

**Symptom:** UE registers but data connectivity fails

**Troubleshooting:**
1. Check SMF is registered with NRF: `docker logs oai-smf 2>&1 | grep -i "nrf"`
2. Verify UPF is functioning: `docker logs oai-upf 2>&1 | tail -20`
3. Check AMF for PDU session establishment messages: `docker logs oai-amf 2>&1 | grep -i "pdu session"`

---

## 9. Issues Encountered and Resolutions

| Issue | Cause | Resolution |
|-------|-------|------------|
| Patch application failed | Repository had uncommitted modifications | Ran `git reset --hard` before applying patch |
| USRP not detected | USB connection not established | Reset USB with unbind/bind procedure |
| SIM not in database | Nothing Phone SIM not registered | Added IMSI 001010000059449 to database |
| AMF tried PDU session before SMF ready | Timing issue | Waited for SMF to fully register with NRF |
| gNB crashes | Various causes (memory, config) | Restart gNB; check logs for root cause |

---

## 10. Current Status

### 10.1 What Works

| Component | Status |
|-----------|--------|
| 5G Core Network (AMF, SMF, NRF, UPF) | ✅ Running |
| gNB Registration with AMF | ✅ Successful |
| USRP Detection | ✅ Verified |
| Nothing Phone SIM in Database | ✅ Registered |
| UE (Nothing Phone) Network Registration | ✅ Connected |
| PWS Patch Applied | ✅ Complete |

### 10.2 In Progress

| Issue | Status |
|-------|--------|
| UE State Cycling | 🔄 Stabilizing |
| PDU Session Stability | 🔄 Debugging |
| Data Connectivity | 🔄 Not yet established |
| Speed Test | ⏳ Pending PDU session |

---

## 11. Key Files and Locations

| File/Directory | Description |
|----------------|-------------|
| `~/openairinterface5g/` | Main OAI 5G RAN repository |
| `~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf` | gNB configuration |
| `~/openairinterface5g/sib8.conf` | SIB8/PWS configuration |
| `~/openairinterface5g/cmake_targets/ran_build/build/nr-softmodem` | gNB executable |
| `~/oai-cn5g/` | 5G Core Network Docker compose |
| `~/oai-cn5g/database/oai_db.sql` | Subscriber database |
| `~/5g-sib8-alert/` | PWS patches and NMS |
| `~/cross-cell-verification/` | Cross-cell verification UE build |
| `~/gnb.log` | gNB log file |

---

## 12. Next Steps

1. **Stabilize PDU Session** - Resolve UE state cycling issue
2. **Establish Data Connectivity** - Get stable internet connection through 5G
3. **Run Speed Test** - Test network performance with OOKLA or similar
4. **Test PWS Functionality** - Send a public warning message through the network
5. **Document Results** - Capture metrics and publish findings

---

## 13. Useful One-Liners

```bash
# Quick status check - all in one
echo "=== USRP ===" && uhd_find_devices && echo "=== Containers ===" && docker ps --format "table {{.Names}}\t{{.Status}}" && echo "=== gNB ===" && ps aux | grep nr-softmodem | grep -v grep && echo "=== UE in AMF ===" && docker logs oai-amf 2>&1 | grep "UEs" | tail -1

# Complete restart sequence
cd ~/oai-cn5g && docker-compose restart && sleep 10 && cd ~/openairinterface5g/cmake_targets/ran_build/build && sudo nohup ./nr-softmodem -O ~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf -E --continuous-tx > ~/gnb.log 2>&1 &
```

---

## 14. Comparison: serber-firecell vs serber-minipc

| Parameter | serber-firecell | serber-minipc |
|-----------|-----------------|---------------|
| PLMN | 001/01 | 001/01 |
| AMF IP | 192.168.70.132 | 10.76.170.45 |
| gNB IP | 192.168.70.129 | 10.85.168.144 |
| Band | 78 | 78 |
| PRB | 106 | 106 |
| Numerology | 1 (30kHz SCS) | 1 |

---

## 15. Conclusion

We have successfully established a working 5G network infrastructure on serber-firecell with PWS capability. The Nothing Phone can now register to the network, marking a significant milestone in our research. The next phase involves stabilizing the PDU session for data connectivity and conducting speed tests to validate network performance.

---

**End of Report**