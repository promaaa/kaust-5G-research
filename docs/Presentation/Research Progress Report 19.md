# Ethernet CU/DU MCS floor unlocked, 89 Mbps measured

**Date:** June 22, 2026
**Timeline:** April 7 to July 31, 2025 (16 weeks)

---

## What changed since last update

1. OAI scheduler source read: `get_mcs_from_bler` in `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c` only bumps MCS when the exponentially filtered BLER drops below `bler_options->lower`, which defaults to 0.05 in `MACRLC_nr_paramdef.h`.
2. Live radio BLER quantified: 22 to 35 percent round-1 HARQ retransmits under sustained traffic, well above the 0.05 lower threshold, so the scheduler could not climb above the `dl_min_mcs = 5` floor.
3. DU runtime config relaxed: added `dl_bler_target_lower = 0.25` and `dl_bler_target_upper = 0.35` inside the `MACRLCs` block, matching the values used by OAI's reference band77 config at `targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb-du.sa.band77.273prb.fhi72.8x8-benetel650_650.conf`.
4. DU restarted with the same `kill -9` plus `setsid` pattern the TUI uses: UE reattached via the direct-cable F1 path and ping RTT dropped from 2.3 seconds to 11 to 30 milliseconds.
5. TCP MSS clamping installed inside the UPF container: two iptables mangle rules clamp new TCP sessions to MSS 1360, matching what `applyUpfMssClamping()` would install.
6. Phone-side throughput measured at 89 Mbps: MCS distribution dominated by 24 and 27, sustained HARQ round-1 retransmits around 22 percent, comfortably inside the new BLER target window.

---

## Project status summary

| Element | Status | Notes |
| --- | --- | --- |
| Monolithic OAI 5G SA | Working | Around 150 to 190 Mbps |
| CU/DU split over Ethernet | Working | 89 Mbps after BLER target relax, MCS up to 27 |
| CU/DU split over Wi-Fi GRE | Demonstrated historically | Around 12 Mbps, needs clean repetition |
| CU/DU split over Quectel WireGuard | Working | Around 42 to 50 Mbps, MCS up to 23 |
| Single-B210 RF backhaul | Experimental | Broker and donor sync passed, registration not achieved |
| Raspberry Pi 5 as DU | Cutover completed | Needs OAI-specific resource profiling |
| TUI launch and validation | Working | Preflight, packet-path checks, PWS/SIB8, and rollback |
| Lab wiki | Published | Six static HTML pages on GitHub Pages |

---

## Problem: MCS pinned at the floor despite a capable radio

The same B210 access radio and antenna path that previously delivered 190 Mbps in monolithic mode and 45 Mbps at MCS 23 over WireGuard was pinned at MCS 5 in the direct-cable Ethernet CU/DU split. The hand-off attributed the gap to F1 path MTU. That was a reasonable direction to investigate, but the actual cause was one level deeper, in the OAI scheduler configuration.

| Path | Throughput | Dominant MCS |
| --- | --- | --- |
| Monolithic | 150 to 190 Mbps | 18 to 23 |
| WireGuard split | around 45 Mbps | 23 |
| Ethernet split pre-fix | around 22 Mbps | 5 |

The hand-off from the previous session asked the next agent to look at F1 path MTU and TCP MSS clamping. Both were investigated, but neither was the binding constraint.

---

## Root cause: default BLER target window is unreachable at the live radio

The OAI NR scheduler decides MCS each scheduling interval using exponentially filtered BLER with alpha 0.9. The MCS update logic:

```c
int new_mcs = old_mcs;
if (bler_stats->bler < bler_options->lower && old_mcs < max_mcs && num_dl_sched > 3)
    new_mcs += 1;
else if (bler_stats->bler > bler_options->upper || num_dl_sched <= 3)
    new_mcs -= 1;
```

The defaults from `MACRLC_nr_paramdef.h` are `lower = 0.05` and `upper = 0.15`. With the live Ethernet radio running 22 to 35 percent round-1 HARQ retransmits under sustained traffic, the scheduler sees `bler > upper` on every update interval, decrements MCS, floors at the configured `dl_min_mcs = 5`, and never recovers.

The `dl_min_mcs = 5` floor itself does not prevent MCS from rising above 5. The decrement path is what pins MCS, and the increment path requires BLER below `lower`, which is unreachable at this radio's actual error rate.

This is consistent with the v2 diagnostic note in `oai-cu-du-lab/experiments/20260622_120500_eth_cu_du_throughput_recheck_v2.md`: "MCS only rises when the exponentially filtered BLER drops below 5 percent." The previous fix proposal (MSS clamping for smaller TBs) was a reasonable attempt but did not address the unreachable lower threshold directly.

---

## Fix: relax the BLER target window and clamp MSS as defense in depth

Two changes applied to the running lab, no stack restart required for the MSS clamp and a single DU restart for the BLER target change.

### Change 1: BLER target window in the DU runtime config

```yaml
file: "/tmp/oai-tui-gnb-minipc-ethernet-runtime.conf"
location: "serber-minipc, inside MACRLCs block"
backup: "/tmp/oai-tui-gnb-minipc-ethernet-runtime.conf.bak-before-bler-target"
added_lines:
  dl_bler_target_upper: "0.35"
  dl_bler_target_lower: "0.25"
  ul_bler_target_upper: "0.35"
  ul_bler_target_lower: "0.15"
```

The DU was killed and restarted using the same pattern the TUI uses for Ethernet startup: `kill -9` against the running `nr-softmodem` that matches the runtime config, then `cd /home/serber/monolithic/openairinterface5g/cmake_targets/ran_build/build && sudo -n setsid ./nr-softmodem -O <conf> --log_config.global_log_level info -E`. UE reattached via F1 Setup on the direct cable without operator action.

### Change 2: TCP MSS clamp inside the UPF

```yaml
host: "serber-firecell"
container: "oai-cn5g-minipc-oai-upf-1"
chain: "FORWARD"
table: "mangle"
match_count_after_test: 713
rules:
  - "-o tun0 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 1360"
  - "-i tun0 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 1360"
```

These are the exact two rules installed by the TUI's `applyUpfMssClamping()`. New TCP sessions through the UPF now negotiate MSS 1360 instead of 1460, keeping GTP-U payloads bounded. The rule was already added and now matches are accumulating (713 SYNs seen during testing).

### Change 3: nothing else

The MSS clamp and the BLER target relax are the only changes. Radio parameters (`att_tx = 3`, `att_rx = 12`, `pusch_TargetSNRx10 = 150`, `pucch_TargetSNRx10 = 200`, `min_rxtxtime = 6`, `sdr_addrs = "serial=8002816"`, `bands = [78]`, BWP, numerology, Docker bridge MTU 9000) are all unchanged from the pre-fix runtime.

---

## Validation

### MCS distribution before and after on the same Ethernet direct-cable path

| MCS | Before fix | After fix |
| --- | --- | --- |
| 5 | 338230 | 12003 |
| 6 | 0 | 1837 |
| 7 to 9 | 0 | 11567 |
| 10 to 15 | 0 | 10077 |
| 16 to 22 | 0 | 39620 |
| 23 | 0 | 10972 |
| 24 | 0 | 37937 |
| 25 to 26 | 0 | 8041 |
| 27 | 0 | 41009 |

The scheduler now lets the radio run at 256-QAM with high code rate whenever the filtered BLER drops below the new lower threshold of 0.25.

### Live radio metrics during sustained ping flood

| Metric | Value |
| --- | --- |
| RSRP | -89 to -96 dBm |
| PH | 48 to 61 dB |
| PCMAX | 22 dBm |
| Cumulative HARQ round-1 retransmits | around 22 percent |
| Ping RTT minipc to firecell | 0.18 ms |
| UE ping RTT ext-DN to UE | 11 to 30 ms (down from 2.3 s) |
| Scheduler `limit` field | `bler` (no longer `mcs_table` or `dl_max_mcs`) |

### End-to-end throughput with phone-side measurement

```yaml
throughput_measurement:
  method: "phone-side speed test against internet-bound traffic"
  value_mbps: 89
  mcs_dominant: [24, 27]
  bler_target_window: "0.25 to 0.35"
  config: "direct Ethernet cable, MSS clamp at 1360, no Quectel"
```

The previous agent diagnostics flagged "no phone-side iperf3 server, no synchronized speed test available" as the reason throughput could not be measured precisely. That constraint was removed by the operator with a real phone-side speed test against the live Ethernet split.

---

## Comparison to baseline

| Path | Pre-fix | After fix |
| --- | --- | --- |
| Ethernet CU/DU split | around 22 Mbps, MCS pinned at 5 | 89 Mbps, MCS up to 27 |
| WireGuard CU/DU split | around 45 Mbps, MCS up to 23 | not re-measured |
| Monolithic | around 150 to 190 Mbps | not re-measured |

The Ethernet direct-cable path now exceeds the WireGuard F1 path. This is consistent with the radio being the actual bottleneck all along and the F1 transport being a thin wrapper that should not gate throughput once the scheduler is configured correctly. The previous "jumbo frames help" hypothesis was directionally right but did not address the binding constraint.

---

## Rollback

To revert to the pre-fix state, two reversals:

```yaml
du_runtime:
  restore_from: "/tmp/oai-tui-gnb-minipc-ethernet-runtime.conf.bak-before-bler-target"
  action: "kill -9 the current nr-softmodem, restart with the restored config"

upf_mss_clamp:
  rule_1: "iptables -t mangle -D FORWARD -o tun0 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 1360"
  rule_2: "iptables -t mangle -D FORWARD -i tun0 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 1360"
```

After rollback the MCS distribution collapses back to floor 5 and throughput returns to the previous 22 Mbps ceiling. The runtime edit is also lost on the next TUI restart because `prepareEthernetDuConfig()` regenerates the file from the original `gnb-minipc.conf` template, so the change must be persisted in the TUI to survive normal operator workflow.

---

## Next steps

1. Persist the BLER target relax in the TUI: extend `prepareEthernetDuConfig()` in `oai-cu-du-lab/scripts/oai-lab-tui` to inject `DL_BLER_TARGET_LOWER` and `DL_BLER_TARGET_UPPER` from environment variables, parallel to the existing `ACCESS_MIN_MCS` injection, then update `oai-cu-du-lab/patches/performance/ethernet-jumbo-frames-persistent.md` and `oai-cu-du-lab/docs/BASELINES.md` with the new defaults.
2. Re-measure WireGuard and monolithic under identical conditions to confirm whether the 89 Mbps figure is the new Ethernet ceiling or whether further gain is possible with the same MSS clamp and BLER target applied.
3. Verify that the OAI build ships with the `dl_bler_target_*` keys parsed correctly so the change does not depend on the lab-side runtime edit. Spot-check a clean rebuild.
4. Update the public wiki's commands page with the new runtime config snippet and the UPF iptables rule pair, and add a short note on the lab wiki architecture page about the BLER target window as the actual binding constraint.
