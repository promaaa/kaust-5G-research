# Synthesis for meeting: backhaul, wiki, Ethernet MCS unlock

**Date:** June 22, 2026
**Timeline:** April 7 to July 31, 2025 (16 weeks)

---

## What changed since last update

1. Single-B210 RF backhaul advanced: native broker served concurrent OAI access and backhaul roles, donor SIB1 decoded via native UHD, but PRACH detection on the donor is still pending (Report 16).
2. Lab wiki published: six static HTML pages deployed to GitHub Pages at `promaaa.github.io/oai-cu-du-lab` with automated CI (Report 17).
3. Ethernet CU/DU MCS floor unlocked: OAI BLER target window relaxed in the DU runtime, 89 Mbps measured phone-side, MCS up to 27 (Report 19).

---

## Project status at a glance

| Path | Throughput | Status | Source report |
| --- | --- | --- | --- |
| Monolithic | 150 to 190 Mbps | Working | carried |
| Ethernet CU/DU split | 89 Mbps | Working | 19 |
| Quectel WireGuard split | 42 to 50 Mbps | Working | carried |
| Single-B210 RF backhaul | not measured end-to-end | Experimental, PRACH detection pending | 16 |
| Lab wiki | live | Public, automated CI | 17 |

---

## Single-B210 RF backhaul (Report 16)

The motivation is to remove the cellular dependency from the lab: replace the Quectel modem with a second USRP B210 chain that carries F1 over the air, while the same B210 continues to serve the Nothing Phone as the access cell on its other chain. If this works, the lab becomes a self-contained 5G testbed with no operator-network requirement.

The hardware quickly constrained the design. Two independent OAI processes cannot each open the B210; the device presents itself as a single multi-channel unit, and both chains share one local oscillator. Splitting the chains across two processes is rejected at the UHD layer. This forced a single-owner architecture: one process drives both chains, and OAI roles consume the IQ streams through a broker.

A native C++ broker was developed to own both chains and serve OAI roles over local sockets. A stabilized run produced:

| Counter | Access | Backhaul |
| --- | ---: | ---: |
| Input blocks | 30,835 | 34,960 |
| Output blocks | 30,843 | 35,020 |
| Timestamp gaps | 0 | 0 |
| RX or TX queue drops | 0 | 0 |

During this run, the access DU completed F1 Setup and received SIB8 while the backhaul UE attempted donor synchronization. This proves shared device ownership and concurrent OAI transport; it does not yet prove RF-carried F1.

The donor downlink was decoded natively using stock `nr-uesoftmodem` directly on the MiniPC: PBCH passed, SIB1 decoded, ten PRACH attempts transmitted. The downlink reaches the MiniPC cleanly at the OAI layer. The blocker is the uplink: the donor never detected PRACH from the MiniPC. Without PRACH detection, registration cannot complete, RAR cannot be received, RRC setup cannot happen, and a PDU session cannot be established. F1 over the radio backhaul therefore remains untested end-to-end.

A rfsimulator-based broker variant consistently failed the SIB1 DL-SCH CRC gate even though native UHD decoded the same SIB1, which shifted the investigation toward a device-layer integration that more closely reproduces the native USRP driver. The replacement now preserves exact RX sample counts, first-sample timestamps, B210 four-bit RX normalization, TX timestamps and burst flags, frequency corrections and retunes, RX and TX gains and bandwidth, and separate control, RX, and TX connections. Both components build against the pinned OAI commit. Native equivalence through PBCH and SIB1 on the new path is the current radio gate.

Key gates from the experiment:

| Gate | Status |
| --- | --- |
| One owner controls both B210 chains | Passed |
| Concurrent real OAI access and backhaul clients | Passed |
| Access F1 Setup and SIB8 while broker is active | Passed |
| Donor PBCH through broker | Passed |
| Donor SIB1 through native UHD | Passed |
| Donor SIB1 through broker | Failed at DL-SCH CRC |
| PRACH detected by donor | Not passed |
| End-to-end RF-carried F1 | Not tested |
| Full single-B210 PASS | Not passed |

---

## Lab wiki (Report 17)

Until this report, the lab had no public entry point. Operators and external readers had to clone the repository and read raw Markdown to understand the project. The wiki closes that gap with six static HTML pages hosted at `promaaa.github.io/oai-cu-du-lab`.

| Page | Contents |
| --- | --- |
| Home | Project overview, key features, and general status |
| Architecture | CU/DU split layouts, WireGuard tunnel, and PWS/SIB8 flow |
| Workflows | Reference deployment, Ethernet, Wi-Fi, and Quectel split steps |
| Hardware | Server, Raspberry Pi, B210, and phone specifications |
| Commands | Executable commands for core, CU, DU, and traffic testing |
| Project info | Baseline rules, testing requirements, and next milestones |

The styling is dark mode with alert styles and a responsive sidebar layout. Deployment is automated through `.github/workflows/pages.yml`, which is triggered on pushes to `main` that modify `wiki/`. A lightweight Python HTTP server provides local preview before publishing.

The wiki is also the natural place to surface future findings. The Ethernet MCS unlock from Report 19 should be added to the commands page once the BLER target relax is persisted in the TUI. The B210 hardware limits and the single-owner constraint from Report 16 should appear in the hardware page so future operators do not waste cycles trying to open both B210 chains from two processes.

---

## Ethernet CU/DU MCS unlock (Report 19)

The Ethernet CU/DU split had been capped at around 22 Mbps with MCS pinned at 5, despite the same B210 reaching MCS 23 in the WireGuard split and MCS 18 to 23 in monolithic mode. The hand-off suggested the F1 path MTU was the bottleneck. The investigation went in the opposite direction.

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

The DU was killed and restarted using the same `kill -9` plus `setsid ./nr-softmodem` pattern the TUI uses for Ethernet startup. UE reattached via F1 Setup on the direct cable without operator action. As defense in depth, two iptables mangle rules were installed in the UPF container to clamp new TCP sessions to MSS 1360.

| Metric | Before fix | After fix |
| --- | --- | --- |
| Dominant MCS | 5 (338 k samples) | 24 (37.9 k), 27 (41 k) |
| Radio BLER | 22 to 35 percent | around 22 percent, inside new window |
| Phone-side throughput | 22 Mbps (cap) | 89 Mbps |
| Ping RTT ext-DN to UE | 2.3 seconds | 11 to 30 milliseconds |

The radio was never the bottleneck. The upstream OAI defaults assumed a cleaner radio than this lab has, and the scheduler was pessimistically pinning MCS in response. The 22 Mbps figure that had been recorded as the Ethernet CU/DU ceiling was a configuration artifact, not a transport limit. Once the threshold was relaxed, the same radio reached MCS 27 with comparable HARQ, and the direct-cable Ethernet path now exceeds the WireGuard F1 path.

---

## Cross-cutting message

The three reports cover three different layers of the lab, and the recurring pattern is the same: upstream OAI defaults assume a cleaner radio than this lab has. The single-B210 PRACH path is blocked because the donor and the access cell are physically closer and less isolated than OAI's reference deployment expects. The Ethernet MCS path was capped because the BLER target window was set for a similar reference link. In both cases, the binding constraint was a configuration default, not a hardware limit, and relaxing the default unlocked the next step.

This argues for treating OAI defaults as starting points that need to be tuned per deployment, and for keeping tuning artifacts (runtime conf edits, iptables rules, broker configurations) close to the lab workflow instead of in one-off fixes.

---

## Next steps

1. Persist the BLER target relax in the TUI (extend `prepareEthernetDuConfig()` in `scripts/oai-lab-tui` to inject `DL_BLER_TARGET_LOWER` and `DL_BLER_TARGET_UPPER` from environment variables, parallel to the existing `ACCESS_MIN_MCS` injection), so the 89 Mbps is not lost on the next operator workflow.
2. Re-measure monolithic, Ethernet split, and WireGuard split under identical conditions with a phone-side speed test, so the new ceilings replace the old ones in `docs/BASELINES.md`.
3. Resume the single-B210 backhaul investigation from the device-layer integration (Report 16 next-steps 2 to 6), starting with PRACH detection on the donor side and chain-A TX connector verification.
