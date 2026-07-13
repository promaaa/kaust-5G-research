# Downlink BLER and MCS adaptation in Ethernet split and monolithic modes

**Date:** June 24, 2026
**Timeline:** April 7 to July 31, 2025 (16 weeks)

---

## What changed since last update

1. Root cause analyzed: identified that GTP-U encapsulation overhead and large Transport Block sizes caused the 22% BLER in Ethernet split mode.
2. Monolithic mode compared: verified that the local monolithic reference mode avoids transport overhead and keeps BLER below the increment threshold.
3. Mitigation implemented: applied TCP MSS clamping in the UPF and adjusted gNB BLER target thresholds to unlock the MCS scheduler.

---

## Source of high BLER in Ethernet split mode

The untuned Ethernet CU/DU split mode experienced a persistent Downlink Block Error Rate (BLER) of 22% to 35% under load. This high error rate resulted from the combination of GTP-U encapsulation overhead and the Transport Block size effect on the physical radio channel.

When user plane traffic is routed over the F1 interface, each IP packet is encapsulated in a GTP-U tunnel, which adds 40 to 50 bytes of header overhead. In a standard network with a path MTU of 1500 bytes, this encapsulation forces IP packets to exceed the MTU, causing fragmentation. Fragmented packets suffer from increased drop rates, raising the overall BLER.

To prevent fragmentation, the path MTU was raised to 9000 bytes. However, this exposed the Transport Block size effect. Without TCP MSS clamping, the TCP stack negotiated a large Maximum Segment Size based on the jumbo frame MTU. The gNB MAC layer scheduled these large segments into very large Transport Blocks on the physical radio channel (up to 14 KB at MCS 5).

In physical wireless transmission, the probability of block corruption increases with block length. Since HARQ operates on the entire Transport Block, a single bit error causes the entire block to fail its CRC check and trigger a NACK. This inflated the real radio BLER to 22% to 35%, well above the OAI default scheduler increment threshold.

---

## Comparison of split and monolithic modes

In monolithic mode, the CU, DU, and core run on the same physical host without an external F1 interface. This configuration bypasses GTP-U encapsulation and avoids transport MTU constraints. The physical layer Transport Blocks remain smaller, resulting in a low radio BLER. This low BLER allows the scheduler to adapt and scale up to high MCS values.

| Mode | F1 interface | TCP MSS clamping | Typical BLER | Dominant MCS | Throughput |
| --- | --- | --- | --- | --- | --- |
| Monolithic | absent | not required | below 5% | 18 to 21 | 150 to 190 Mbps |
| Split (untuned) | direct GbE | none | 22% to 35% | 5 | 12 to 22 Mbps |
| Split (tuned) | direct GbE | MSS 1360 | around 22% | 24 to 27 | 100 Mbps peak |

---

## Scheduler adaptation parameters

The OAI scheduler dynamically adjusts the Downlink MCS based on the exponentially filtered BLER. The adjustment logic in `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c::get_mcs_from_bler` requires the filtered BLER to drop below `bler_options->lower` to increment the MCS.

The default configuration uses the following values:

```yaml
default_bler_options:
  dl_bler_target_lower: 0.05
  dl_bler_target_upper: 0.15
  dl_min_mcs: 0
```

Since the real radio BLER under untuned split mode remained at 22% to 35%, it never fell below the 5% lower threshold. The scheduler repeatedly decremented the MCS until it hit the configured minimum floor of `dl_min_mcs = 5`.

To unlock the scheduler, TCP MSS clamping was applied inside the `oai-cn5g-minipc-oai-upf-1` container to limit TCP segment size to 1360 bytes, reducing the physical Transport Block size. Additionally, the BLER target parameters were adjusted in the DU runtime configuration at `/tmp/oai-tui-gnb-minipc-ethernet-runtime.conf`:

```yaml
MACRLCs:
  dl_bler_target_upper: 0.35
  dl_bler_target_lower: 0.25
  ul_bler_target_upper: 0.35
  ul_bler_target_lower: 0.15
```

These adjusted targets allow the scheduler to increment the MCS when the filtered BLER is below 25%, enabling the system to run at MCS 24 to 27.

---

## Next steps

1. Perform sustained user-plane throughput tests with a commercial phone.
2. Integrate the adjusted BLER target thresholds into the default TUI configuration scripts.
3. Validate the tuned parameters over the wireless F1 backhaul path.
