
**Date:** June 21, 2026
**Timeline:** April 7 to July 31, 2025 (16 weeks)

---

## What changed since last update

1. State of the art consolidated
2. Single-B210 RF backhaul advanced: native broker served concurrent OAI access and backhaul roles, donor SIB1 decoded via native UHD, but PRACH detection on the donor is still pending.
3. Lab wiki published: six static HTML pages deployed to GitHub Pages at `promaaa.github.io/oai-cu-du-lab` with automated CI.
4. Ethernet CU/DU MCS floor unlocked: OAI BLER target window relaxed in the DU runtime, 89 Mbps measured phone-side, MCS up to 27.
5. TUI adaptability added: the operator TUI now adapts to a new setup with different IP addresses and machines without code changes.

---

## State of the art and added value

The literature reviewer falls into six areas. While other testbeds exist, they are notoriously difficult to reproduce, rely on expensive customized infrastructure, and do not support emergency alert dissemination over disaggregated components. 

Our work differentiates itself by focusing on off-the-shelf, low-cost hardware and being the first to build an easily reproducible testbed, as well as being the first to successfully broadcast PWS messages over a CU/DU split (via the F1 interface).

- **OAI and open-source 5G platforms.** OAI RAN, OAI 5GC, F1, and CI-CD pipelines are widely documented. Our use of off-the-shelf, commodity hardware paired with our TUI and automated reproducibility pipeline is the key differentiator.
- **CU/DU split and F1.** 3GPP Option 2 with F1-C on SCTP and F1-U on GTP-U is standardized. However, ours is the first testbed to enable and validate PWS broadcasting across disaggregated CU/DU boundaries.
- **Wireless or non-ideal midhaul.** IAB, aerial DU on OAI, NTN and satellite midhaul have been studied. Our Wi-Fi GRE plus commercial 5G plus WireGuard combination is not documented. And the comparison of 5G/WIFI/Ethernet for F1 link is not documented.
- **PWS and SIB8.** While 5G emergency alerts have been integrated into monolithic OAI systems (e.g., for security/spoofing research), we are the first to successfully route and broadcast PWS messages (SIB8) through a disaggregated CU/DU split over the F1 interface, validated on a commercial Phone.
- **Lightweight or edge 5G.** srsRAN on Pi 5 is demonstrated by Pi5G. Running an OAI DU on Pi 5 with heterogeneous F1 and off-the-shelf components is new.
- **Reproducibility and testbed methodology.** NIST O-RAN automation is valued but relies on complex server environments. Our testbed is specifically built on accessible, off-the-shelf hardware and is the first to prioritize community reproducibility via a TUI (preflight, packet placement validation, and rollback).

Four contributions are genuinely additive:
1. F1 heterogeneous transport comparison using off-the-shelf hardware under a shared protocol, with packet placement validation.
2. MCS collapse analysis and recovery through a concrete OAI scheduler parameter change (BLER window).
3. The first end-to-end demonstration of PWS over a real CU/DU split (F1 interface), validated on a commercial Nothing Phone.
4. The first OAI CU/DU split testbed designed specifically for easy reproducibility, packaging preflight, packet placement validation, and rollback into a clean Operator TUI.

The strongest single sentence we can defend today is:

> We built the first easily reproducible OAI CU/DU split testbed utilizing low-cost, off-the-shelf hardware, characterized three heterogeneous F1 transport paths (resolving an MCS collapse), and achieved the first end-to-end broadcast of PWS warning messages over a disaggregated CU/DU split (F1 interface) validated on a commercial handset.

two directions stay preliminary: single-B210 RF backhaul end-to-end, and the drone-carried or portable DU use case (concept only).

---

## Project status at a glance

| Path                    | Throughput              | Status                                | Source report |
| ----------------------- | ----------------------- | ------------------------------------- | ------------- |
| Monolithic              | 150 to 190 Mbps         | Working                               | 15            |
| Ethernet CU/DU split    | 89 Mbps                 | Working                               | 19            |
| Quectel WireGuard split | 42 to 50 Mbps           | Working                               | 15            |
| Wi-Fi GRE split         | around 12 Mbps          | Demonstrated, needs clean repetition  | 15            |
| Single-B210 RF backhaul | not measured end-to-end | Experimental, PRACH detection pending | 16            |
| Lab wiki                | live                    | Public, automated CI                  | 17            |
| Pi 5 DU                 | Cutover completed       | Needs OAI-specific resource profile   | 15            |

---

## Single-B210 RF backhaul

We wanted to remove the cellular dependency from the lab: replace the Quectel modem with a second USRP B210 chain that carries F1 over the air, while the same B210 continues to serve the Nothing Phone as the access cell on its other chain. If this works, the lab becomes a self-contained 5G testbed with no operator-network requirement.

The hardware quickly constrained the design. Two independent OAI processes cannot each open the B210; the device presents itself as a single multi-channel unit, and both chains share one local oscillator. Splitting the chains across two processes is rejected at the UHD layer. This forced a single-owner architecture: one process drives both chains, and OAI roles consume the IQ streams through a broker.

| Counter | Access | Backhaul |
| --- | ---: | ---: |
| Input blocks | 30,835 | 34,960 |
| Output blocks | 30,843 | 35,020 |
| Timestamp gaps | 0 | 0 |
| RX or TX queue drops | 0 | 0 |


---

## Lab wiki 

The wiki hosted at: promaaa.github.io/oai-cu-du-lab enables anyone via a very succinct and simple way to understand more about the project and how to interact with it.

| Page         | Contents                                                       |
| ------------ | -------------------------------------------------------------- |
| Home         | Project overview, key features, and general status             |
| Architecture | CU/DU split layouts, WireGuard tunnel, and PWS/SIB8 flow       |
| Workflows    | Reference deployment, Ethernet, Wi-Fi, and Quectel split steps |
| Hardware     | Server, Raspberry Pi, B210, and phone specifications           |
| Commands     | Executable commands for core, CU, DU, and traffic testing      |
| Project info | Baseline rules, testing requirements, and next milestones      |

---

## Ethernet CU/DU MCS unlock

The Ethernet CU/DU split had been capped at around 22 Mbps with MCS pinned at 5, despite the same B210 reaching MCS 23 in the WireGuard split and MCS 18 to 23 in monolithic mode. 

Reading the OAI source showed that the NR scheduler only bumps MCS when the exponentially filtered BLER drops below `bler_options->lower`, which defaults to 0.05 in `MACRLC_nr_paramdef.h`. The live Ethernet radio runs 22 to 35 percent round-1 HARQ retransmits under sustained traffic, well above 0.05. The scheduler therefore saw `bler > upper` on every update interval, decremented MCS, floored at the configured `dl_min_mcs = 5`, and never recovered.

The fix was to relax the BLER target window to match OAI's reference band77 config. Four lines were added to the DU runtime conf inside the `MACRLCs` block:

```yaml
file: "/tmp/oai-tui-gnb-minipc-ethernet-runtime.conf"
location: "serber-minipc, inside MACRLCs block"
added_lines:
  dl_bler_target_upper: "0.35"
  dl_bler_target_lower: "0.25"
  ul_bler_target_upper: "0.35"
  ul_bler_target_lower: "0.15"
```


| Metric                | Before fix    | After fix             |
| --------------------- | ------------- | --------------------- |
| Dominant MCS          | 5             | 24-27                 |
| Radio BLER            | 22-35%        | around 22%            |
| Phone-side throughput | 22 Mbps (cap) | 89 Mbps               |
| Ping RTT ext-DN to UE | 2.3 seconds   | 11 to 30 milliseconds |

The 22 Mbps figure that had been recorded as the Ethernet CU/DU ceiling was a configuration artifact, not a transport limit. Once the threshold was relaxed, the same radio reached MCS 27 with comparable HARQ, and the direct-cable Ethernet path now exceeds the WireGuard F1 path.


---

## TUI Adaptability 

Now the TUI can easily adapt to a new setup with different ip addresses and machines.
![[Pasted image 20260623103127.png]]

---

## Next steps

1. Move to Jetson Orin nano
2. Re-measure monolithic, Ethernet split, and WireGuard split, Wifi split under identical conditions with a phone-side speed test.
3. BLER
4. USRP B210 
5. Keep working on the LateX wiki
