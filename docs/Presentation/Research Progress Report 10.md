**Date:** May 19, 2026
**Timeline:** April 7 to July 31, 2025 (16 weeks)

---

## What changed since last update

1. WiFi GRE backhaul transported F1-C and F1-U over wifi between CU and DU, replacing the ethernet link
2. WiFi GRE tunnel a
3. achieved ~12 MB/s UE throughput, roughly 60% of the ethernet baseline
4. Monolithic gNB plus nrUE tested end-to-end over USRP B210 on band n78
5. Full internet access over 5G NR validated with no ethernet or WiFi in the data path
6. Code modification of the transmission of SIB8
7. PWS reception validation on Nothing Phone
 
---

## Problem: replace ethernet F1 backhaul with wireless

The CU/DU split relied on ethernet for the F1 interface between serber-firecell and serber-minipc. We needed to transport F1-C (SCTP) and F1-U (GTP-U) over a wireless medium without modifying OAI configs or restarting processes.

| Host     | Outer Local   | Outer Remote  | Inner IP      | Device          |
| -------- | ------------- | ------------- | ------------- | --------------- |
| firecell | 10.76.170.38  | 10.85.168.144 | 10.255.0.1/30 | test-gre@enp6s0 |
| minipc   | 10.85.168.144 | 10.76.170.38  | 10.255.0.2/30 | test-gre@wlp3s0 |


---

## Symmetric Routing Fix

**Problem:** minipc sent GRE return packets directly via enp2s0 ethernet because `10.76.170.38` was in the same subnet, making the tunnel asymmetric.

**Solution:** Added a host route on minipc forcing all traffic to firecell through the WiFi gateway:

```bash
ip route add 10.76.170.38/32 via 10.85.175.254 dev wlp3s0
```



---

## Policy Routing: zero-downtime migration

Used Linux policy routing to force existing F1 sockets through the tunnel without touching OAI configs:

```bash
# firecell
ip rule add from 10.76.170.38 lookup 100
ip route add 10.76.170.100/32 dev test-gre table 100

# minipc
ip rule add from 10.76.170.100 lookup 100
ip route add 10.76.170.38/32 dev test-gre table 100
```

The SCTP/GTP-U 4-tuple never changed, so applications were unaffected and the UE never disconnected.

---

## Tunnel traffic verification

| Host | Interface | TX | RX |
|------|-----------|----|----|
| firecell | test-gre@enp6s0 | 383.5 MB | 44.4 MB |
| minipc | test-gre@wlp3s0 | 44.4 MB | 385.8 MB |

The 383 MB TX from firecell and 385 MB RX at minipc was almost entirely F1-U (GTP-U user plane). This confirmed both F1-C and F1-U were successfully offloaded to the WiFi tunnel.

---

## Results

| Metric        | Ethernet F1     | WiFi GRE Backhaul |
| ------------- | --------------- | ----------------- |
| UE throughput | 19–23 MB/s      | ~12 MB/s          |
| DL BLER       | 0.05%           | ~0.06–0.12%       |
| UL BLER       | 0%              | 0%                |
| F1 SCTP       | Connected       | Connected         |
| UE state      | 5GMM-REGISTERED | 5GMM-REGISTERED   |

The wireless backhaul delivered roughly 60% of ethernet throughput with zero downtime. The bottleneck was WiFi shared infrastructure.

---


## Problem: full IP connectivity over the NR radio link

Can a PC running OAI nrUE with only a USRP B210 receive a real IP connection and access the internet through a 5G radio link? 


**Hardware and radio configuration**

| Host            | Role       | Band / PRB    | Frequency  |
| --------------- | ---------- | ------------- | ---------- |
| serber-firecell | gNB + CN5G | n78 / 106 PRB | 3619.2 MHz |
| serber-minipc   | nrUE       | n78 / 106 PRB | 3619.2 MHz |

**gNB radio parameters**

| Parameter | Value |
|-----------|-------|
| absoluteFrequencySSB | 641280 |
| dl_absoluteFrequencyPointA | 640008 |
| dl_carrierBandwidth | 106 PRB |
| ul_carrierBandwidth | 106 PRB |
| max_rxgain | 114 |
| att_tx / att_rx | 3 / 12 |
| ssPBCH_BlockPower | -25 |
| max_pdschReferenceSignalPower | -27 |
| clock_src | internal |

**Registration and PDU Session Verification**

gNB logs confirmed: UE detected via PRACH, RRC Setup and Reconfiguration Complete, NGAP Initial UE Message, PDU Session Resource Setup, GTP-U tunnel created.

AMF container logs confirmed: Registration Request from SUPI 001010000059449, 5GMM REGISTERED, PDU session establishment accept sent.

UE logs confirmed: Cell synchronization achieved, RRC connection established, NAS Registration Accept received, PDU session accepted, tunnel interface `oaitun_ue1` created with IP address 10.0.0.x.


---

## Connectivity test reachability

1. UPF reachability: ping -I oaitun_ue1 192.168.71.129
 2. Public IP ping: ping -I oaitun_ue1 8.8.8.8
 3. HTTP download: curl --interface oaitun_ue1 -v --max-time 20 http://example.com
 4. File download: wget --bind-address 10.0.0.x -O /dev/null http://speedtest.tele2.net/1MB.zip

All tests were run with explicit interface binding to `oaitun_ue1` to confirm no ethernet or WiFi was in the data path.

---

## Results

| Metric | Value |
|--------|-------|
| UE registration | 5GMM REGISTERED |
| PDU session | Established |
| Tunnel interface | oaitun_ue1 present |
| UE IP address | 10.0.0.x from UPF |
| Ping UPF | OK |
| Ping 8.8.8.8 | OK |
| HTTP through NR | OK |
| Failure mode | None, all phases succeeded |

The feasibility question was answered. A PC running OAI nrUE with a USRP B210 can receive real IP connectivity through a 5G radio link from another PC running OAI monolithic gNB plus CN5G. The UE host was fully disconnected from ethernet and WiFi for user-plane traffic, and still accessed the public internet over the NR radio link.

---

## SIB8 transmission modification and PWS validation

The PWS/SIB8 path was updated so the warning message can be generated by the CU, forwarded across the F1 interface, and transmitted by the DU over the NR cell. This keeps the public warning broadcast aligned with the CU/DU split architecture instead of only working in a monolithic gNB setup.

**Transmission path**

| Stage | Component  | Role                                                               |
| ----- | ---------- | ------------------------------------------------------------------ |
| 1     | CU RRC     | Reads `sib8.conf` and prepares the warning message contents        |
| 2     | CU F1AP    | Encodes the message as a `WRITE_REPLACE_WARNING_REQUEST`           |
| 3     | DU F1AP    | Decodes the warning request and passes the SIB8 payload toward MAC |
| 5     | DU MAC/PHY | Schedules and broadcasts SIB8 over the radio interface             |
| 6     | UE         | Receives the PWS alert from the live NR cell                       |

The implementation wires the DU-side warning handler, fixes buffer ownership while forwarding the SIB8 payload, and makes decode failures explicit so invalid SIB8 data is not silently scheduled.

**Nothing Phone validation**

The Nothing Phone was used as a real UE to confirm that the modified SIB8 path is visible outside the lab software stack. After the cell was on air, the phone detected the private 5G network and received the PWS alert broadcast from the gNB.

| Check | Result |
|-------|--------|
| Nothing Phone detects 5G cell | Pass |
| UE remains attached while PWS is sent | Pass |
| SIB8/PWS message reaches the phone | Pass |
| End-to-end path CU to DU to UE | Validated |

This confirms that the SIB8 modification is not only present in the logs, but produces an observable PWS alert on a commercial handset.

---

## Next Steps

1. **Full 5G backhauling:** Run iperf3 from minipc (UE) to measure actual end-to-end throughput over the NR radio link.

2. **Deploy the split between oai-pc and serber-firecell:** Make sure to identify if the bottleneck comes from the F1 link
