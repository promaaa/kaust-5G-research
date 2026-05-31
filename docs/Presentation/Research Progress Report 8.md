
**Date:** May 12, 2026
**Timeline:** April 7 – July 31, 2025 (16 weeks)

---

## What Changed Since Last Update

Debug session on May 12, 2026 identified the root cause of the "no internet" issue despite 5G bars showing on the UE.

---

### Root Cause: Radio Downlink is Broken

| Direction | BLER | Errors | DTX | MCS |
|---|---|---|---|---|
| **Uplink (UE → gNB)** | 0% | 0 | 2/7781 | Working fine |
| **Downlink (gNB → UE)** | **74%** | 57 | 626 | MCS 0 (pinned to minimum) |

The UE uploads 7× more data than it downloads (TX 29,604 bytes vs RX 206,676 bytes — asymmetry inverted). Control plane (SRB1, NAS) survives because small messages + HARQ retries handle 74% BLER. User-plane DRB packets are larger and break TCP/HTTPS handshakes to `connectivitycheck.gstatic.com`, causing Android to report "no internet."

### Data Plane is Healthy (Verified)

| From → To | Result |
|---|---|
| oai-ext-dn → UPF eth0 | 0% loss |
| oai-ext-dn → 8.8.8.8 | 0% loss, ~66ms |
| oai-upf → 1.1.1.1 with UE subnet source | 0% loss, ~66ms |

UPF SNAT, host MASQUERADE, and DOCKER-FORWARD/CT all show matching counter deltas end-to-end. **The NAT/routing/Docker path is correct.**

---

#### **Current setup**

| Machine | IP | Role |
|---|---|---|
| serber-firecell | 10.76.170.38 | CU + Core Network |
| serber-minipc | 10.76.170.100 | DU (B210, serial 35F8ABA) |
| serber-pi | 10.76.170.94 | DU (B210, serial 8002816) |

**Pi 5 hardware:** Cortex-A76, 4 GB RAM

---


### IP Configuration

Pi only has one interface on the 10.76.170.0/25 subnet (`10.76.170.94`), so both F1-C and F1-U use that same IP:

```
cu:
  f1c_ip: 10.76.170.94
  f1u_ip: 10.76.170.94
  remote_f1c_ip: 10.76.170.38
```

This was the key issue. I initially tried to use `10.76.170.102` for F1-U, but that IP doesn't exist on Pi, causing GTP-U bind failure.

---

## Pi 5 Performance as DU

| Metric       | Value                      |
| ------------ | -------------------------- |
| CPU load     | 2.04 (4 cores), 54.8% idle |
| RAM used     | 1.5 GiB / 4.0 GiB          |
| Temperature  | 67.0°C                     |
| CPU throttle | None                       |
| Underruns    | 0                          |


No struggles detected. Pi 5 handles DU workload (MAC + RLC + PHY) without issue at 51 PRB.

---

## F1 Link Status

 **CU (serber-firecell) Log:**
```
F1AP   CU Task Received F1_SETUP_REQUEST from gNB_DU 3584 (gNB-CU-FIRECELL)
NR_RRC Accepting DU 3584 (gNB-CU-FIRECELL), sending F1 Setup Response
NR_RRC cell PLMN 001.01 Cell ID 12345678 is in service
F1AP   CU Task Received F1AP_WRITE_REPLACE_WARNING
```

 **PI (serber-pi) Log:**
```
NR_MAC Frame.Slot 0.0
NR_MAC Frame.Slot 128.0
NR_MAC Frame.Slot 256.0
F1AP   DU Task Received SCTP_NEW_ASSOCIATION_RESP
F1AP   DU_send_F1_SETUP_REQUEST
F1AP   received F1 Setup Response from CU gNB-CU-FIRECELL
```

F1 link established


---

## Summary

| What Works              | Status |
| ----------------------- | ------ |
| serber-pi as DU (Pi 5)  | OK     |
| F1 link (CU ↔ Pi)       | OK     |
| Pi 5 hardware stability | OK     |
| B210 on Pi              | OK     |
| Repo cleanup            | OK     |
| serber-minipc DU        | OK     |

**Next steps:**
Fix radio downlink BLER (currently 74%)
Validate UE internet connectivity after radio fix

---

## Issues Fixed This Session

### 1. CU Config Syntax Error
`~/cu-du/source/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb-cu.conf` line 33:
```
mcc = "1"   ← SYNTAX ERROR (must be integer, no quotes)
mcc = 1     ← CORRECT
```
**Fix:** Use the working config at `~/monolithic/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb-cu.conf` instead.

### 2. CU Dies on Shell Exit
Interactive launches (e.g., `sudo ./nr-softmodem ...`) die with SIGHUP when the shell closes.
**Fix:** Launch CU with `setsid nohup ... &` or as a systemd unit.

### 3. CU → Core Startup Order
If the 5G core isn't up before the CU, the CU loops in NGAP retry.
**Fix:** Bring up core (`docker compose up -d`) before starting the CU.

---

## Confirmed NOT the Cause (do not investigate)

- Host MASQUERADE — firing correctly
- UPF SNAT (10.0.0.0/24 → 192.168.70.134) — counter deltas match end-to-end
- DOCKER-FORWARD/CT — packet counts symmetric
- cu-du config's `mcc = "1"` — broken but irrelevant when using monolithic config
- Prior GTP error indications (TEID 0x5/0xb/0xc) — teardown artifacts, not live flow
- 10.0.0.1/24 conflict on enp6s0 — already removed

---

## Current System State (May 12, 2026 ~13:09)

| Component | Status |
|---|---|
| CU (firecell) | PID 3439887 alive, SCTP 10.76.170.38:38472 |
| 5G Core | All containers healthy (AMF, SMF, UPF, NRF, UDR, UDM, AUSF, ext-dn, ims, mysql) |
| DU (serber-pi) | alive, UE RNTI 0165 in-sync, PH 44 dB, PCMAX 22 dBm |
| DU (serber-minipc) | alive, UE in-sync |
| AMF | UE 001010000059449 5GMM-REGISTERED |
| UPF | PFCP SEID 0x2 active, UE IP 10.0.0.2 |

---

## Recommended Actions (Radio Focus)

Since the user said "do not touch radio config", these are recommendations for the next agent:

1. **DL TX power / gain at DU** — With MCS 0 pinned and 74% BLER, downlink lacks sufficient EIRP or has too much attenuation. Uplink at same site is 0% BLER with SNR 17 dB, so the asymmetry is in the gNB→UE direction.
2. **UE physical position** — Move the Nothing Phone closer to the gNB antenna.
3. **Antenna / cable on DU TX path** — Check SMA, cable condition, dB pads on TX only.
4. **RF interference in DL band** — Less likely given clean uplink in shared TDD band.

Until DL BLER drops below ~10% initial / ~1% final, internet from the UE will not work regardless of datapath configuration.