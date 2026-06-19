s# TUI capabilities and demonstration plan

**Date:** June 16, 2026
**Timeline:** April 7 to July 31, 2025 (16 weeks)

---

## What changed since last update

1. TUI fully working
2. Quectel outer transport measured: the Quectel 5G backhauling system now provides about 50 Mbps as the outer transport layer for wireless F1
3. Raspberry Pi 5 cutover completed: the operator TUI now targets `serber-firecell` + `serber-pi` as the primary access DU endpoint
4. TUI adapted for Pi DU discovery, preflight, and launch
5. LaTeX documentation started: `docs/overleaf/main.tex` consolidates the deployment history, current topology, reproducible procedures.

---

## Raspberry Pi 5 deployment

I completed the cutover from `serber-minipc` to `serber-pi` as the primary access DU endpoint. The following work was done:

| Check                                        | Purpose                             |
| -------------------------------------------- | ----------------------------------- |
| `hostname`, `ip -4 -br addr`, `ip route get` | host identity and route to firecell |
| `nproc`, `free -h`                           | CPU cores and memory                |
| `vcgencmd measure_temp`                      | Pi thermal state                    |
| `uhd_find_devices --args serial=8002816`     | B210 presence and FPGA loaded       |
| `ls /dev/cdc-wdm* /dev/ttyUSB*`              | Quectel modem availability          |
| `git rev-parse HEAD`                         | OAI commit pin                      |


**Ethernet Pi CU/DU launch: OK**

Packet placement confirmed:

```text
Pi DU eth0: SCTP heartbeats between 10.76.170.18 and 10.76.170.38
firecell enp6s0: matching SCTP heartbeats
Pi wlan0: no F1 packets
Pi wwan0: no F1 packets
Pi wg-quectel-f1: no F1 packets
```

**Quectel Pi backhaul launch: OK**

The TUI gates passed for hardware, core, subscriber, configs, donor gNB, registration, quectel, routes, wireguard, donor validation, CU, DU, packet placement, and UE/F1-U.

---
## TUI overview

The operator console is a single dependency-free Node.js script:

```bash
./scripts/oai-lab-tui
```

---

## TUI capabilities

**Main menu actions**

![[Pasted image 20260613122740.png]]


### Hardware discovery

The TUI discovers hosts at runtime:

| Host | Target | Role |
|------|--------|------|
| `serber-firecell` | `serber@10.76.170.38` | Fixed management target for CU, core, and donor gNB |
| `serber-minipc` | Discovered dynamically | Access DU on `serber-minipc` |

Discovery includes USRP B210 detection (serial `8002816` for access cell), Quectel QMI device (`/dev/cdc-wdm0`) and PDU session state, live management interface and routing table inspection, and WireGuard handshake status and bidirectional tunnel ping.

### PWS/SIB8 message manager

The PWS/SIB8 manager updates every TUI-managed warning-message config in one operation:

- firecell monolithic OAI
- firecell split and caged CU OAI
- live minipc split and caged DU OAI
- compatibility copies under the related scenario roots and `conf/` directories

The TUI records the updated remote paths in the local evidence directory for the message update. A scenario restart is still required before the new warning text is broadcast, because OAI reads `sib8.conf` during process startup.

### Experimental preflight helpers

The following workflows remain in the script but are hidden from the main operator menu for now. Should we include them in the definitive TUI?

- Raspberry Pi DU preflight
- `oai-pc` DU preflight
- nrUE internet-through-radio preflight
- older Quectel showcase checks

---

## Gate sequences

![[Pasted image 20260613122948.png]]

The Ethernet startup action gates the run in this order:

1. Host and minipc discovery
2. Previous OAI softmodem stop
3. Conflicting monolithic core stop
4. Competing `oai-pc` F1 isolation
5. DU B210 detection
6. Split core startup
7. DU runtime config generation
8. CU startup
9. DU startup
10. F1 and PWS milestone validation
11. Packet validation
12. Phone prompt and core health

The Ethernet scenario prints **PASS** only after F1 setup, SIB8/PWS delivery, DU radio sync, F1-C SCTP on the discovered Ethernet interfaces, and no F1-C or F1-U leakage on WiFi, Quectel, or WireGuard interfaces are visible.

---
![[Pasted image 20260607105147.png]]

The monolithic scenario prints **PASS** only after these gates pass:

- Firecell B210 is detected
- Monolithic core containers start
- Monolithic gNB process remains running
- AMF and gNB NG setup is visible
- SIB8/PWS and radio sync are visible in the monolithic gNB log
- No live minipc DU, split-core containers, Ethernet split F1, or `wg-quectel-f1` F1 traffic remains visible

---

**Caged Quectel F1 backhaul**

![[Pasted image 20260613123802.png]]
The Quectel scenario gates the run in this order:

1. Hardware preflight
2. Firecell core
3. Quectel subscriber provisioning in the active split core
4. Generate CU/DU configs using the external generator script
5. Start firecell monolithic donor gNB
6. Quectel donor registration reset and validation of PCI 1 and TAC 2
7. Quectel QMI and PDU
8. Routes
9. WireGuard
10. Validate independent donor path (PCI, TAC, IP, routes, ping gates)
11. Start firecell CU bound to `10.250.0.1`
12. Start minipc access DU over WireGuard
13. Packet validation
14. UE and F1-U validation and rollback readiness

The scenario prints **PASS** only after all required packet gates pass:

- F1-C SCTP is visible on `wg-quectel-f1`
- WireGuard outer UDP is visible on the discovered Quectel data interface
- F1-U `UDP/2153` is visible on `wg-quectel-f1` during phone traffic
- Discovered management Ethernet and WiFi interfaces carry no F1-C or F1-U during validation windows

The UE and F1-U gate gives the operator three phone-traffic attempts. If no `UDP/2153` appears on `wg-quectel-f1`, the TUI fails closed and records `No PASS claimed`.

---

## Throughput baselines by configuration

![Throughput by configuration](throughput_chart%201.png)

Short justification: Ethernet should normally be the faster and cleaner backhaul than a 5G/WireGuard path. The 42 Mbps Quectel result show that the Quectel launch escaped the old split-mode bottleneck. The access radio stayed the same, but the clean launch moved F1 onto `wg-quectel-f1`, refreshed routes/WireGuard state, and avoided stale scheduler or feedback state. The live DU log confirms this: unlike older Ethernet split runs where DL MCS was pinned at `0`, the Quectel run climbed to high DL MCS values, including `MCS 27`.

### MCS observations

- **Monolithic**: DL MCS reaches 18 to 23 under sustained load
- **Ethernet split**: DL MCS has been observed pinned at `0` under sustained load, likely due to scheduler and feedback path issues. This is under investigation.
- **Quectel backhaul**: DL MCS is no longer stuck at `0`; live access-DU logs show non-zero and high-MCS operation, including `MCS 27`.

---

## LaTeX documentation

A LaTeX document was started at to consolidate the deployment history, current hardware topology, reproducible operating procedures, validation rules, and measured results. The document will be structured as a technical handoff intended for a new intern and as a basis for a future research paper.

![[Pasted image 20260616095439.png]]



## Next Steps

1. Finalize the documentation
2. Try setting up the new kernel for Jetson and eventually deploy our config on it
3. Finalize the TUI with phone-attached throughput recording and DU initial-access evidence hooks 
4. Gather every differences possible between our work and the already published papers
5. Make an adaptable TUI 
6. Calcul puissance poids et choix du drone
