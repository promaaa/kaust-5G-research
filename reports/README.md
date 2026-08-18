# Progress Reports & Experimental Notebook

This directory contains the 22 chronological laboratory reports documenting 16 weeks of research on the airborne OpenAirInterface 5G CU/DU disaggregated testbed.

> **Operational Context:**  
> Deployment automation and configuration templates are maintained in the companion operational repository: [`promaaa/oai-cu-du-lab`](https://github.com/promaaa/oai-cu-du-lab).

---

## Report Index

The numbered reports below serve as a chronological lab notebook. Early reports preserve interim hypotheses, while later reports (Reports 18–22) contain the validated findings and final architectural resolutions.

| Report | Date | Primary Focus & Milestones |
| :--- | :--- | :--- |
| [**Report 02**](report-02.md) | Apr 15 | OAI core deployment, Docker environment, and Jetson SCTP constraints |
| [**Report 03**](report-03.md) | Apr 22 | CU/DU split bring-up and direct Ethernet baseline planning |
| [**Report 04**](report-04.md) | Apr 29 | USRP B210 hardware validation and Raspberry Pi 5 DU feasibility |
| [**Report 05**](report-05.md) | May 02 | Raspberry Pi 5 benchmarking and softmodem thread pool tuning |
| [**Report 06**](report-06.md) | May 05 | Commercial UE (Nothing Phone) integration and PWS baseline |
| [**Report 07**](report-07.md) | May 08 | CU/DU split deployment and PWS debugging |
| [**Report 08**](report-08.md) | May 12 | Radio failure isolation, RF attenuation, and Pi 5 performance |
| [**Report 09**](report-09.md) | May 15 | User-plane data recovery and Pi 5 runtime tuning |
| [**Report 10**](report-10.md) | May 19 | Wi-Fi/GRE F1 backhaul and PWS/SIB8 commercial handset validation |
| [**Report 11**](report-11.md) | May 29 | Quectel 5G modem / WireGuard F1 bring-up and circular dependency discovery |
| [**Report 12**](report-12.md) | Jun 05 | Bottleneck analysis, wireless backhaul, and Pi DU evaluation |
| [**Report 13**](report-13.md) | Jun 10 | MCS analysis, donor cell topology separation, and RF isolation |
| [**Report 14**](report-14.md) | Jun 16 | Operator TUI deployment tooling and transport baselines |
| [**Report 15**](report-15.md) | Jun 20 | State of the art (SOTA) review and project positioning |
| [**Report 16**](report-16.md) | Jun 22 | State of the art synthesis and experimental value proposition |
| [**Report 17**](report-17.md) | Jun 23 | Dedicated RF backhaul, lab wiki, and MCS recovery |
| [**Report 18**](report-18.md) | Jun 24 | Downlink BLER/MCS root cause (GTP-U MTU fragmentation vs TCP MSS clamping) |
| [**Report 19**](report-19.md) | Jul 02 | Tuned Ethernet baseline (100 Mbps), USRP X310 evaluation, Jetson Orin Nano DU integration |
| [**Report 20**](report-20.md) | Jul 08 | USRP X310 bandwidth retest (10 GbE requirement), embedded benchmarks |
| [**Report 21**](report-21.md) | Jul 12 | Power, mass, and Jetson validation benchmarks |
| [**Report 22**](report-22.md) | Jul 16 | Jetson 5G backhaul recovery (~40 Mbps), full mathematical drone & battery sizing models |

---

## Late-Stage Breakthroughs Summary

Reports 18–22 supersede the early interim hypothesis that a ~23 Mbps throughput ceiling was an inherent limitation of the CU/DU split:
1. **TCP MSS Clamping (1360 bytes):** Eliminated GTP-U IP packet fragmentation and reduced MAC Transport Block size, dropping physical BLER.
2. **OAI Scheduler Tuning:** Adjusting `dl_bler_target_lower: 0.25` and `dl_max_mcs: 28` unlocked higher modulation orders (`MCS 24–27`).
3. **Jetson Orin Nano Optimization:** Custom SCTP kernel, `MAXN_SUPER` mode, `jetson_clocks`, and USB-C SuperSpeed enumeration enabled stable ~40–44 Mbps over Quectel 5G WireGuard backhaul.

---

## Presentation Sources

- [`french-project-presentation.md`](french-project-presentation.md) — Retained speaker-oriented presentation source derived from the notebook. Can be rendered using Obsidian with the Advanced Slides plugin.
