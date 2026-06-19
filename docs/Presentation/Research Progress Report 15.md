# State of the art and project positioning

**Date:** June 18, 2026
**Timeline:** April 7 to July 31, 2025 (16 weeks)

---

## What changed since last update

1. State of the art reviewed: two deep-research reports were synthesized around OAI, CU/DU split, F1 transport, PWS/SIB8, and portable 5G testbeds.
2. Project positioning clarified: our work is not only an OAI deployment, but a complete experimental platform combining split RAN, heterogeneous F1 transport, packet-path validation, and PWS/SIB8.
3. Main overlap identified: OAI testbeds, CU/DU split, wireless backhaul, and PWS experiments already exist separately in the literature.
4. Main difference identified: the combination of OAI CU/DU split, Wi-Fi GRE, Quectel 5G with WireGuard, TUI validation, Raspberry Pi 5 DU, and PWS/SIB8 appears much less documented.
5. Evidence gap clarified: the next work should focus on controlled comparison, root-cause analysis, and clean validation rather than adding more features.

---

## Purpose of this report

This report is a support document for the discussion with the professor.

The goal is not yet to decide the exact publication venue. The goal is to answer three questions:

1. What has already been done by other researchers?
2. What have we already built and measured?
3. Where is the real difference between the state of the art and our project?

The short answer is:

> The literature already contains OAI testbeds, CU/DU split deployments, wireless or remote DU scenarios, emergency alert experiments, and lightweight 5G platforms. Our project is interesting because it combines these directions into one reproducible OAI platform, with heterogeneous F1 transport paths and packet-level proof of where the traffic goes.

---

## Current project summary

| Element                                    | Current status            | Why it matters                                                       |
| ------------------------------------------ | ------------------------- | -------------------------------------------------------------------- |
| Monolithic OAI 5G SA                       | Working                   | Gives a clean baseline for throughput, radio behavior, and PWS/SIB8. |
| OAI CU/DU split over Ethernet              | Working                   | Gives the standard split baseline.                                   |
| OAI CU/DU split over Wi-Fi GRE             | Demonstrated historically | Tests F1 over a non-ideal wireless transport.                        |
| OAI CU/DU split over Quectel and WireGuard | Working, at 50 Mbps       | Tests F1 over a commercial 5G modem and VPN tunnel.                  |
| Raspberry Pi 5 as DU                       | Cutover completed         | Tests whether the access DU can be moved to edge hardware.           |
| TUI launch and validation                  | Working                   | Makes the setup repeatable and safer to operate.                     |
| Packet placement checks                    | Integrated in TUI gates   | Proves that F1-C and F1-U use the intended network path.             |
| PWS/SIB8 manager                           | Integrated in TUI         | Gives an emergency-alert use case for the split architecture.        |
| MCS and throughput observations            | Under investigation       | May reveal why some split runs collapse while others recover.        |

---

## State of the art map

The reviewed literature can be grouped into six areas.

| Area | What the state of the art already covers | What it means for our project |
| --- | --- | --- |
| OAI and open-source 5G testbeds | OAI is widely used for 5G RAN, core network, SDR, and experimental research. | Running OAI alone is not enough to be considered new. |
| CU/DU split and F1 | CU/DU split is already implemented and studied in OAI, O-RAN, and 3GPP-based research. | A working split is a necessary baseline, not the whole contribution. |
| Wireless or non-ideal midhaul | Remote DU, wireless backhaul, IAB-like systems, aerial DU, and satellite or cellular transport have been studied. | Our Wi-Fi GRE and Quectel WireGuard paths should be compared to this family of work. |
| Reproducible testbeds | Recent papers emphasize scripts, automation, datasets, clean setup descriptions, and repeatability. | Our TUI, preflight gates, rollback, and packet validation are valuable in this direction. |
| PWS and emergency alerts | PWS, SIB8, and emergency alert experiments exist, including recent OAI-based work. | PWS itself is not new, but PWS in a real OAI CU/DU split remains a strong positioning point if validated. |
| Lightweight or edge 5G | Raspberry Pi 5 and small-form-factor 5G testbeds have been explored, often with srsRAN. | Pi 5 is useful for the edge story, but we need OAI-specific resource measurements. |

---

## Detailed comparison with existing work

| Existing direction | Typical focus | Difference with our project |
| --- | --- | --- |
| Standard OAI 5G SA testbeds | Bring up OAI RAN and core with SDR and UE. | We go beyond bring-up by comparing monolithic and split modes across several transport paths. |
| OAI CU/DU split experiments | Validate F1 setup and split operation, often over Ethernet. | We treat F1 transport as the experimental variable, not just the connection between CU and DU. |
| O-RAN and open RAN platforms | Study disaggregation, automation, RIC integration, and sometimes multi-vendor components. | Our work is more focused on practical F1 path behavior in an OAI software-defined setup. |
| Aerial DU or remote DU papers | Move the DU away from the CU, often for emergency or coverage extension use cases. | Our remote DU is connected through specific tested paths: Ethernet, Wi-Fi GRE, and Quectel WireGuard. |
| Wireless backhaul and IAB studies | Study wireless relay or backhaul feasibility, often at system or simulation level. | Our setup is a real OAI implementation with SDR, commercial UE, modem, packet captures, and operator tooling. |
| PWS and alert spoofing testbeds | Study emergency alert generation, spoofing, or UE behavior. | Our PWS/SIB8 story is tied to the split architecture and F1 delivery path. |
| Raspberry Pi 5 5G testbeds | Show that lightweight 5G deployments can run on Pi 5 class hardware. | Our Pi 5 role is specifically an OAI DU in a CU/DU setup with heterogeneous F1 transport. |

---

## What is already covered by others

These points should be presented carefully because they are not unique by themselves.

```yaml
already_known:
  - "OAI can be used to run 5G SA testbeds"
  - "CU/DU split over F1 exists and is supported in OAI"
  - "F1-C uses SCTP and F1-U uses GTP-U over UDP"
  - "Remote and wireless DU scenarios have been explored"
  - "Public warning systems and SIB8 have been studied"
  - "Small edge hardware can host parts of a 5G testbed"
  - "Automation and reproducibility are important for open RAN experiments"
```

This does not weaken the project. It helps define the correct level of claim.

---

## What we bring

The project contribution is the combination and the experimental control around it.

| Contribution | What we bring concretely | Why it is useful |
| --- | --- | --- |
| Integrated OAI platform | Monolithic, split Ethernet, split Wi-Fi GRE, split Quectel WireGuard, and Pi 5 DU scenarios. | Enables direct comparison across architectures and transport paths. |
| Heterogeneous F1 transport | F1 is transported through clean Ethernet, Wi-Fi GRE, and commercial 5G with WireGuard. | Tests conditions closer to deployable emergency or tactical networks. |
| Packet-path proof | The TUI checks where F1-C, F1-U, WireGuard outer traffic, and management traffic appear. | Avoids false conclusions caused by traffic using the wrong interface. |
| Operator TUI | Preflight, launch, validation, scenario gates, and rollback are centralized. | Makes the platform reusable and easier to demonstrate. |
| Performance observations | Monolithic reaches around 150 Mbps, older split runs were around 19 to 23 Mbps, Wi-Fi GRE around 12 Mbps, Quectel WireGuard around 42 to 50 Mbps. | Shows that transport and launch state may strongly affect split performance. |
| MCS observations | Monolithic MCS reaches around 18 to 23, some split runs were pinned at 0, and Quectel runs have reached high MCS such as 27. | Suggests a deeper interaction between transport, scheduler behavior, and radio feedback. |
| PWS/SIB8 integration | The warning-message configuration is managed across scenarios, including split deployments. | Gives the testbed a meaningful emergency-network use case. |
| Pi 5 DU cutover | The access DU can be targeted on Raspberry Pi 5. | Supports a portable or edge DU narrative. |

---

## What is most different from the state of the art

The most distinctive parts are not isolated features. They are combinations.

| Combination | Why it is distinctive |
| --- | --- |
| OAI CU/DU split plus Quectel 5G plus WireGuard | This is a practical F1-over-commercial-5G scenario, not only Ethernet split. |
| OAI CU/DU split plus Wi-Fi GRE | This tests a simple non-ideal wireless F1 transport path that is rarely documented in detail. |
| F1 transport comparison plus MCS and BLER observations | This connects network transport to radio-layer behavior. |
| TUI plus packet placement validation | This makes the experiment more trustworthy and repeatable. |
| PWS/SIB8 plus CU/DU split | This links emergency warning delivery to a disaggregated RAN path. |
| Pi 5 DU plus heterogeneous F1 transport | This supports an edge deployment scenario with real resource constraints. |

The strongest current positioning is:

```yaml
positioning:
  "A reproducible OAI CU/DU experimental platform for comparing heterogeneous F1 transport paths and validating split-compatible emergency-network behavior."
```

---

## Performance comparison so far

These numbers should be presented as current observations, not final scientific conclusions.

| Configuration | Observed throughput | Observed MCS behavior | Current interpretation |
| --- | --- | --- | --- |
| Monolithic OAI | Around 150 Mbps | MCS around 18 to 23 | Radio path and hardware are capable of good performance. |
| Split Ethernet, older runs | Around 19 to 23 Mbps | Sometimes pinned at 0 | There is a split-specific or run-state-specific bottleneck to explain. |
| Split Wi-Fi GRE | Around 12 Mbps | Needs clean repeated measurement | Non-ideal transport likely hurts performance, but the result needs repetition. |
| Split Quectel WireGuard | Around 42 to 50 Mbps | High MCS observed, including MCS 27 | The old split bottleneck is not inevitable and may depend on setup state or transport behavior. |

The important point for the professor is:

```yaml
interpretation:
  wrong_shortcut: "The split is always bad"
  better_statement: "The split can behave very differently depending on transport, routing, launch state, scheduler state, and radio feedback"
  next_question: "Which factor explains the collapse in the bad runs?"
```

---

## Why the MCS observation matters

The MCS behavior is one of the most important technical observations because it links the network experiment to the radio stack.

| Observation | Meaning |
| --- | --- |
| Monolithic MCS is high and stable | The access radio and UE can sustain good link adaptation. |
| Some split runs have MCS pinned at 0 | The issue is not simply weak hardware or weak radio. |
| Quectel split can recover high MCS | The split architecture itself is not necessarily the limiting factor. |
| Throughput and MCS vary across transport scenarios | F1 transport and software state may affect radio scheduling indirectly. |

The missing step is to prove causality:

```yaml
needs_proof:
  - "Is the MCS collapse caused by F1-U delay or jitter?"
  - "Is it caused by packet loss, MTU, or fragmentation?"
  - "Is it caused by stale OAI scheduler or feedback state?"
  - "Is it caused by CPU saturation on the DU?"
  - "Is it caused by radio variation despite similar hardware?"
```

---

## PWS/SIB8 positioning

PWS/SIB8 should be presented as a use case and architecture validation point.

| Question | Current answer |
| --- | --- |
| Is PWS/SIB8 itself new? | No. Public warning and SIB8 mechanisms are standardized and recent OAI-based alert experiments exist. |
| What is interesting in our project? | The warning path is considered in a CU/DU split context, where the CU and DU communicate through F1. |
| What must be clarified? | The exact 3GPP procedure, OAI implementation path, F1 message path, and UE-visible behavior. |
| How should it be presented? | As a meaningful emergency-network use case for the testbed, not as the only contribution. |

Recommended wording:

```yaml
pws_claim:
  "We use PWS/SIB8 as an application-level validation case for the split testbed. The key point is not only generating a warning message, but understanding how warning delivery behaves in a CU/DU architecture with heterogeneous F1 transport."
```

---

## Reproducibility and tooling

The TUI is valuable because it changes the project from a fragile manual setup into a repeatable experimental platform.

| TUI function | Research value |
| --- | --- |
| Hardware discovery | Confirms the correct hosts, SDRs, modem, and routes are present. |
| Scenario launch | Makes monolithic, Ethernet split, and Quectel split easier to reproduce. |
| Preflight gates | Reduces false starts and inconsistent experiment states. |
| Packet validation | Proves that the intended transport path is actually used. |
| PWS/SIB8 manager | Keeps warning-message configuration consistent across scenarios. |
| Rollback readiness | Makes demos and repeated tests safer. |

The TUI should not be described only as a convenience tool. It is part of the evidence pipeline.

---

## Remaining gaps

| Gap | Why it matters | Needed action |
| --- | --- | --- |
| Controlled repetitions | Current numbers are observations, not yet statistics. | Run the same experiment at least 10 times per scenario. |
| Fixed OAI commit | Different commits can change performance and behavior. | Freeze one commit for all comparisons. |
| Fixed radio conditions | MCS depends on RF quality. | Use same UE position, cage, coax, or prove stable SNR and CQI. |
| F1 timing analysis | Throughput alone does not explain the bottleneck. | Capture F1-C, F1-U, RTT, jitter, loss, and MTU. |
| Scheduler evidence | MCS collapse must be tied to logs and counters. | Extract MCS, BLER, HARQ, NPRB, SNR, and CQI over time. |
| Pi 5 resource profile | Edge deployment must prove CPU, RAM, and temperature limits. | Log CPU, RAM, and thermal behavior during runs. |
| UE-visible PWS validation | A warning config is not enough. | Show how the UE receives or reacts to the warning. |

---

## Suggested presentation storyline

The professor presentation can follow this order:

1. Start with the problem: disaggregated 5G needs realistic F1 transport, not only clean Ethernet.
2. Show the state of the art: OAI, CU/DU split, wireless backhaul, PWS, and edge testbeds already exist separately.
3. Show our system: one platform combines monolithic, split Ethernet, Wi-Fi GRE, Quectel WireGuard, Pi 5 DU, TUI, packet validation, and PWS/SIB8.
4. Show the first results: monolithic around 150 Mbps, older split Ethernet around 19 to 23 Mbps, Wi-Fi GRE around 12 Mbps, Quectel WireGuard around 42 to 50 Mbps.
5. Explain the key mystery: why does MCS collapse in some split runs but recover in others?
6. Define the next research step: controlled comparison and root-cause analysis.
7. Conclude with the project value: a reproducible experimental platform to study non-ideal F1 transport and emergency-network behavior.

---

## One-slide summary

```yaml
state_of_the_art:
  - "OAI testbeds exist"
  - "CU/DU split exists"
  - "Wireless backhaul and remote DU exist"
  - "PWS/SIB8 experiments exist"
  - "Lightweight 5G testbeds exist"

our_work:
  - "Combines OAI CU/DU split with heterogeneous F1 transport"
  - "Tests Ethernet, Wi-Fi GRE, and Quectel 5G with WireGuard"
  - "Validates packet placement instead of assuming the traffic path"
  - "Integrates PWS/SIB8 as an emergency-network use case"
  - "Adds TUI-based preflight, launch, validation, and rollback"
  - "Moves the DU toward Raspberry Pi 5 edge deployment"

next_research_question:
  "What causes the throughput and MCS collapse in some split scenarios, and how does F1 transport quality influence it?"
```

---

## Next Steps

1. Prepare a compact state-of-the-art slide with the six research areas.
2. Prepare a comparison table showing existing work versus our system.
3. Make a clean architecture figure showing CU, DU, access radio, Quectel, WireGuard, and packet paths.
4. Re-run monolithic, split Ethernet, Wi-Fi GRE, and Quectel WireGuard under identical conditions.
5. Collect throughput, RTT, jitter, loss, MCS, BLER, SNR, CQI, NPRB, HARQ, CPU, RAM, and temperature.
6. Produce one figure comparing throughput by scenario.
7. Produce one figure showing MCS over time by scenario.
8. Clarify the exact PWS/SIB8 path in OAI and across F1.
9. Keep publication strategy as a later discussion after the state-of-the-art comparison and validation campaign are clean.
