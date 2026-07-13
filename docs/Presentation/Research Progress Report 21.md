
**Date:** July 8, 2026
**Timeline:** April 7 to July 31, 2025 (16 weeks)

---

## What changed since last update

1. USRP X310 migration was added: 106 PRB is blocked by the current 1 GbE transport path, while the reduced 51 PRB profile reached F1/PWS/RF-ready before stopping at the Msg3 access-cell boundary.
2. Jetson Orin Nano phone service improved: the Jetson DU now reaches phone-visible PWS, 5G registration, PDU session creation, and handset internet.
3. Jetson throughput remains below baseline: phone speed improved from no internet to about `6.5 Mbps`, then `7.3 Mbps`, but this is still below the Raspberry Pi and MiniPC Ethernet baselines.
4. A stale core service-discovery fault was isolated: AMF could not select SMF until the SMF container was restarted and re-registered with NRF.
5. The remaining Jetson bottleneck was narrowed: core routing and PDU sessions are alive, while evidence points to Jetson radio/runtime jitter, USB/RF overflows, UE responsiveness, and active F1 still using the integrated 1 GbE NIC.
6. The Report 19 Jetson result was rechecked: changing the hub fixed the obvious B210 USB-speed concern, but it did not remove the low-throughput problem.
7. Drone sizing was reframed: the payload model now includes the formula, not only the final tables.
8. The validated B210 baseline was preserved: B210 remains the current access-radio reference, while B205mini-i is only a lightweight future candidate.
9. The procurement recommendation was made more budget aware: Matrice 400 remains the safest full-payload platform, but a cheaper staged path exists if the first flight uses Jetson-class compute instead of the full mini-PC payload.
10. The next validation gates were clarified: close X310 transport, stabilize Jetson throughput, payload weighing, real power measurement, and drone dummy-load testing.
11. The X310 result was compared against Report 19: changing the Ethernet cable path and moving the X310 from `serber-minipc` to `oai-pc` did not remove the 106 PRB overflow problem.

---

## Summary

This week connected three parts of the same portability question. First, the USRP X310 was evaluated as a stronger access radio, but the current host path cannot sustain the transport needed for 106 PRB. Second, the Jetson Orin Nano was explored as a lighter DU host, and it has now moved from machine-side proof to real handset service, although at lower throughput than the Pi and MiniPC. Third, the drone payload work translated those hardware choices into mass, power, battery, and drone-selection consequences.

The main result is that the first airborne configuration should not carry the heaviest version of the lab setup if the goal is budget control. The full mini-PC plus B210 plus Quectel payload still points to a 6 kg-class drone such as DJI Matrice 400. A more budget-friendly path is to fly the Jetson plus B210 plus Quectel validation payload first, but only after the Jetson throughput gap is understood well enough for a stable demonstration. Compared with Report 19, the Jetson path is more proven because the phone now has service after the SMF/NRF fix, but the throughput conclusion is unchanged: changing the hub did not bring Jetson up to the Raspberry Pi or MiniPC Ethernet baselines.

---

## Current architecture

| Element | Role |
| --- | --- |
| Ground 5GC and CU | Runs on `serber-firecell` |
| Donor DU | Provides the independent cell for the Quectel modem |
| Airborne or remote access DU | Runs on mini-PC, Jetson, Pi, or another candidate host |
| Quectel modem | Provides wireless F1 backhaul from access DU to ground CU |
| Access radio | B210 remains the validated baseline, X310 is the high-bandwidth candidate |

The Quectel modem must attach to an independent donor cell. It cannot depend on the same access cell that the airborne DU is trying to backhaul.

```yaml
invalid_same_cell_loop:
  access_du_needs: F1 backhaul
  f1_backhaul_needs: Quectel PDU session
  quectel_pdu_needs: serving 5G cell
  invalid_case: Quectel attaches to the same access cell that requires F1
```

---

## USRP X310 exploration

The USRP X310 was tested as a stronger access-radio candidate, mainly to escape the B210 bandwidth and USB constraints. The current limitation is not the CU or core. The limiting factor is the radio transport path between the host and X310.

| Item | State |
| --- | --- |
| Access radio | USRP X310 |
| Current host path | 1 GbE |
| Target wide profile | 106 PRB |
| Reduced profile | 51 PRB |
| CU/core state | F1 setup and PWS path reached |
| Main blocker | X310 transport and access-cell stability |

At 106 PRB, the X310 path failed with UHD receive overflows and RFNoC timeout behavior. Even with the `-E` reduced-sample-rate mode, the raw radio stream still exceeded what the current 1 GbE path can safely carry. A real 106 PRB X310 retry therefore needs a proven 10 GbE host/NIC path before more RF tuning is meaningful.

The 51 PRB X310 profile is more promising. It avoided the immediate 106 PRB transport wall and reached F1/PWS/RF-ready state, but it still did not close the phone-visible attach path. The remaining blocker is around random access and Msg3, not core reachability.

### Comparison with Research Progress Report 19

Research Progress Report 19 already identified the first X310 boundary on `serber-minipc`. In that earlier test, the X310 access cell could reach higher-layer milestones, including F1 setup and PWS/SIB8 scheduling, but the 106 PRB radio stream failed on the 1 GbE MiniPC-to-X310 path.

The new `oai-pc` attempt was designed to test a different hypothesis. If the MiniPC host, the old Ethernet cable, or a weak physical link was the main cause, then moving the X310 to `oai-pc` and using the spare Intel I225 port should have improved the result. That did not happen. The radio still negotiated only 1 GbE, jumbo MTU was not stable, and both 106 PRB sample-rate modes failed after the X310 reached RF-ready state.

| Item | Report 19 result | Report 21 follow-up |
| --- | --- | --- |
| DU host | `serber-minipc` | `oai-pc` |
| X310-facing path | MiniPC Ethernet path | `oai-pc enp3s0` spare port |
| Cable or port change | original X310 path | X310 moved to `oai-pc` path |
| Negotiated link | 1 GbE | 1 GbE |
| Jumbo MTU | not a solution | `8000` and `9000` dropped the link |
| 106 PRB with `-E` | `46.08 MSps`, overflow and RFNoC timeout | `46.08 MSps`, RF-ready, overflow and RFNoC timeout |
| Native 106 PRB | `61.44 MSps`, immediate overflow | `61.44 MSps`, RF-ready, sustained overflow |
| Phone validation | not reached | not reached |
| Main conclusion | 106 PRB is blocked by X310 transport | same blocker remains after cable and host-path change |

The key result is that changing the Ethernet cable path did not remove the problem. The evidence no longer points to a simple bad-cable explanation, and it also does not point mainly to MiniPC CPU capacity. The common factor across Report 19 and this follow-up is that the available X310 path still behaves like a 1 GbE transport path.

The next X310 106 PRB test should therefore start with physical transport proof before OAI:

```yaml
x310_next_gate:
  negotiated_link_speed: above_1GbE
  stable_mtu: jumbo_or_other_high_throughput_mode
  uhd_frame_size: larger_than_1472
  uhd_streaming:
    reduced_106_prb_E: stable_46_08_MSps
    native_106_prb: stable_61_44_MSps
  f1_path:
    du_to_cu_reachability: required
    sctp_state: established
```

This comparison also keeps the 51 PRB result in context. Report 19 showed that 51 PRB is the closer X310 path because it can reach F1/PWS/RF-ready and then fails later at Msg3. Report 21 does not replace that conclusion. It confirms that 106 PRB should not be the next debugging target until the X310 transport path is upgraded or proven above 1 GbE.

---

## Jetson Orin Nano DU exploration

Jetson is important because it changes the drone equation. A Jetson-class DU is lighter and more power efficient than the mini-PC payload, but it requires more platform tuning than x86. The recent work moved Jetson beyond startup evidence. It now has phone-visible service, but throughput is still not at the level of the Pi or MiniPC baselines.

| Area | Result |
| --- | --- |
| Kernel | SCTP required custom Jetson kernel work |
| OAI build | Native build possible after memory and parallelism control |
| B210 transport | USB 3.0 path required, `5000M` is the real gate |
| Runtime tuning | `MAXN_SUPER`, `jetson_clocks`, CPU performance mode, `usbfs_memory_mb=1000` |
| CPU layout | DU pinned to CPUs `1-5`, CPU `0` left for USB/kernel work |
| Machine-side state | F1 setup, F1-U mapping, B210 on USB SuperSpeed |
| Phone-visible state | PWS received, UE registered, PDU session created, internet reached |
| Current throughput | About `7.3 Mbps` phone speed test |
| Remaining gate | Match or approach Pi and MiniPC stability and throughput |

The tuned Jetson launch shape is:

```yaml
jetson_runtime:
  power_mode: MAXN_SUPER
  clocks: jetson_clocks
  usbfs_memory_mb: 1000
  b210_usb_speed: 5000M
  du_cpu_affinity: "1-5"
  usb_irq_cpu: "0"
  softmodem_shape: "taskset -c 1-5 ./nr-softmodem -O runtime.conf --log_config.global_log_level warning -E"
```

This makes Jetson a good candidate for the first budget-controlled flight payload. It should not yet be treated as performance validated, because the phone now has service but the throughput and latency stability are still below the Pi and MiniPC baselines.

### Jetson throughput problem

The current Jetson problem is no longer basic attach or basic internet. The phone can receive PWS, register to the lab cell, obtain a PDU session, and pass traffic. The problem is that the observed phone throughput is still much lower than the Raspberry Pi and MiniPC Ethernet results.

The sequence was:

| Stage | Observation |
| --- | --- |
| Initial new-hub rerun | PWS path worked, but no fresh UE row or data session was visible |
| Phone report | PWS was received, but the phone did not show 5G service |
| Core diagnosis | UE registration appeared, but AMF could not select SMF |
| Core fix | Restarted only the SMF container, which re-registered with NRF |
| Post-fix network state | SMF and UPF created IMS-like and data sessions |
| Phone result | Internet returned, first around `6.5 Mbps`, later around `7.3 Mbps` |

The core-side issue was a stale NRF/SMF discovery state. AMF received PDU-session requests for `ims` and `oai`, but NRF returned no SMF candidate. The SMF configuration already advertised the expected DNNs, so the problem was not an APN typo. Restarting only SMF caused it to re-register with NRF, advertise the correct DNN list, discover UPF, and complete PFCP association.

```yaml
core_fix:
  symptom: AMF could not select SMF
  cause: NRF discovery returned no SMF candidate
  action: restart only oai-smf
  result:
    - SMF re-registered with NRF
    - AMF selected SMF for ims and oai
    - UPF installed session rules
    - UE data IP became reachable
```

After this fix, the user-plane path became alive. External-DN ping to the live UE data IP reached `0%` packet loss in later checks. However, latency was unstable, with RTT spikes up to about `602 ms`, and the DU accumulated overflows.

| Metric | Current Jetson result |
| --- | --- |
| Phone PWS | Passed |
| UE registration | Passed |
| Data PDU session | Passed after SMF restart |
| External-DN ping | `0%` packet loss in later checks |
| Phone throughput | Improved to about `7.3 Mbps` |
| DU overflows | Increased to `23` during validation |
| RTT behavior | Unstable, with large spikes |
| Compared to Pi/MiniPC | Still lower throughput |

This means the remaining problem is not the 5GC route or the basic F1-U path. The evidence now points to Jetson runtime and radio stability:

1. The B210 stayed on USB SuperSpeed at `5000M`, so the radio is no longer on the earlier USB2 failure path.
2. Jetson stayed in `MAXN_SUPER`, with performance governors and locked clocks, so basic power mode is not the immediate blocker.
3. The DU log still shows `ERROR_CODE_OVERFLOW`, repeated UE context modification activity, and occasional UE responsiveness problems.
4. The ASIX USB Ethernet adapter is present on the SuperSpeed hub, but its network interface has no carrier.
5. The active F1 path is still the integrated Jetson `enP8p1s0` interface at `1000Mb/s`, not the ASIX USB Ethernet path.

```yaml
current_jetson_hypothesis:
  core_path: alive
  pdu_session: alive
  phone_internet: alive
  remaining_bottleneck:
    - radio_runtime_jitter
    - USB_or_RF_overflows
    - UE_context_churn
    - latency_spikes
    - active_F1_on_integrated_1GbE_not_ASIX
```

The important lesson is that Jetson is now a real candidate, but it is not yet a drop-in replacement for the Pi or MiniPC. It needs one more focused optimization pass before it should be used as the main airborne DU compute option.

### Comparison with Report 19

Report 19 already showed the Jetson throughput problem in the host benchmark table. The tuned Ethernet split result on `serber-jetson` was `7.3 Mbps`, while the same table showed `21 Mbps` on the Raspberry Pi and `89 Mbps` on the MiniPC. That earlier result made Jetson attractive mechanically, but not yet performance-equivalent.

The new hub test was meant to recheck the simplest hardware hypothesis behind that gap. In Report 19, the Jetson section identified the B210 USB transport as a critical gate and explained that the radio had to operate at USB 3.0 speed. The current rerun improves that part of the evidence: the B210 stayed on the SuperSpeed tree at `5000M`. However, the phone throughput problem persisted. The latest phone speed moved from about `6.5 Mbps` to about `7.3 Mbps`, which essentially reproduces the Report 19 Jetson number instead of closing the gap to the Pi or MiniPC.

| Item | Report 19 result | Current Report 21 result |
| --- | --- | --- |
| Jetson role | Integrated as a lightweight DU candidate | Still a candidate, but throughput is not baseline-level |
| B210 radio path | USB 3.0 at `5000M` was required for stable 106 PRB operation | New hub keeps B210 at `5000M`, so the USB2 fallback suspect is reduced |
| Tuned Ethernet split on Jetson | `7.3 Mbps` | About `6.5 Mbps`, then about `7.3 Mbps` |
| Raspberry Pi comparison | `21 Mbps` tuned Ethernet split | Jetson remains well below this baseline |
| MiniPC comparison | `89 Mbps` tuned Ethernet split | Jetson remains far below this baseline |
| Phone service | PWS validated, internet noted but speed test was not the focus | PWS, registration, PDU session, and internet now pass |
| Core path | Not identified as the throughput limiter | SMF/NRF fault fixed, external-DN ping reaches `0%` loss |
| Remaining problem | Jetson throughput outlier relative to Pi and MiniPC | Runtime and radio jitter, overflows, latency spikes, active F1 on 1 GbE |

The key conclusion is therefore negative in an important way: the problem did not disappear after changing the hub. The hub made the experiment cleaner by proving that the B210 can stay on USB3, but it did not make Jetson behave like the Pi or MiniPC. The remaining bottleneck is deeper than a simple USB2 fallback, because the current `7.3 Mbps` result matches the earlier Report 19 Jetson result.

```yaml
report_19_to_21_delta:
  confirmed:
    - Jetson can provide phone-visible service
    - B210 can remain on USB3 through the new hub
    - core user-plane can be restored after SMF re-registration
    - current Jetson throughput reproduces the earlier 7.3 Mbps class
  still_not_solved:
    - throughput remains below Pi and MiniPC
    - latency spikes remain visible
    - DU overflows still appear
    - active F1 path is integrated 1GbE, not ASIX USB Ethernet
  conclusion: Jetson is viable but not performance-equivalent yet
```

---

## Drone sizing formula

The model separates payload electronics from the drone propulsion battery. It estimates whether the DU payload fits a drone class, not exact aircraft endurance.

For a configuration $S$:

| Symbol | Meaning |
| --- | --- |
| $m_i$ | Mass of component $i$, in grams |
| $P_i$ | Electrical power of component $i$, in watts |
| $x_i(S)$ | 1 if component $i$ is included, otherwise 0 |
| $t_\mathrm{mission}$ | Payload electronics runtime target |
| $r_\mathrm{reserve}$ | Electrical reserve multiplier |
| $\eta_\mathrm{dc}$ | DC/DC conversion efficiency |
| $u_\mathrm{battery}$ | Usable fraction of nominal battery capacity |
| $\gamma_\mathrm{payload}$ | Maximum fraction of drone payload rating used by our payload |

Fixed payload mass:

$$
m_\mathrm{fixed}(S)=\sum_i x_i(S)m_i
$$

Payload power:

$$
P_\mathrm{payload}(S)=\sum_i x_i(S)P_i
$$

Required nominal electronics battery energy:

$$
E_\mathrm{nom}(S)=
\frac{P_\mathrm{payload}(S)t_\mathrm{mission}r_\mathrm{reserve}}
{\eta_\mathrm{dc}u_\mathrm{battery}}
$$

Selected real battery:

$$
b^\*(S)=
\arg\min_b E_b
\quad
\mathrm{such\ that}
\quad
E_b\ge E_\mathrm{nom}(S)
\quad
\mathrm{and}
\quad
I_b\ge \frac{P_\mathrm{payload}(S)}{V_b}
$$

Total payload mass and minimum drone rating:

$$
m_\mathrm{payload}(S)=m_\mathrm{fixed}(S)+m_{b^\*}
$$

$$
C_\mathrm{required}(S)=
\frac{m_\mathrm{payload}(S)}{\gamma_\mathrm{payload}}
$$

With $\gamma_\mathrm{payload}=0.70$, the payload should use no more than 70% of the advertised drone payload rating. This is a lab margin rule for heat, altitude, mounting hardware, RF cables, antenna separation, mistakes, and future small additions.

---

## Sizing assumptions

```yaml
mission:
  payload_runtime_minutes: 20
  electrical_reserve_factor: 1.30
  usable_battery_fraction: 0.80
  dc_efficiency: 0.88
  max_payload_rating_utilization: 0.70
```

The payload electronics battery is separate from the drone propulsion battery. It powers the DU electronics, SDR, Quectel modem, fans, and DC conversion only.

---

## Computed payload configurations

| ID | Configuration | Payload mass | Required drone rating | Planning Matrice 400 flight |
| --- | --- | ---: | ---: | ---: |
| A | Minimum proof: Pi 5, B205mini-i, Quectel kit | 0.94 kg | 1.34 kg | 40.7 min |
| B | B210 validation: Jetson-class compute, B210, Quectel kit | 1.59 kg | 2.27 kg | 38.3 min |
| C | Actual mini-PC class: x86 mini-PC, B210, Quectel kit | 2.36 kg | 3.37 kg | 35.4 min |
| D | Dual-radio or instrumentation prototype | 3.01 kg | 4.30 kg | 33.0 min |

Configuration B is the best first airborne validation target. It keeps the proven B210 access-radio baseline but replaces the heavier mini-PC with Jetson-class compute. Configuration C is closest to the current mini-PC deployment, but it needs a larger drone if the 70% margin rule is respected.

---

## Drone and budget options

The budget question has two answers:

1. If the payload must be Configuration C or D, DJI Matrice 400 remains the cleanest lower-risk platform because it supports a 6 kg payload class.
2. If the first flight can use Configuration B, the project can use a cheaper validation platform before buying the larger drone.

| Platform                 |                                             Public payload reference |                                                    Budget position | Fit under 70% rule                                | Interpretation                                                                                                                 |
| ------------------------ | -------------------------------------------------------------------: | -----------------------------------------------------------------: | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Tarot X8-Lite prototype  |                                 2 kg load reference, 22 min estimate |                   Frame about $319.90, full build cost not turnkey | A yes, B borderline, C no                         | Cheapest lab prototype path, but requires custom build, flight controller, batteries, safety review, and pilot risk acceptance |
| Tarot X8 11 kg AUW build |                                  10 to 11 kg all-up-weight reference | Lower than enterprise drones, but build cost depends on components | A and B likely, C only after real AUW calculation | Budget engineering platform, not a procurement-ready research drone                                                            |
| DJI Matrice 350 RTK      | 5.9 lb or about 2.7 kg max payload, with 960 g single-damper caution |                              Listed around  7,630$ by one reseller | A and B yes, C no                                 | Budget-friendly only for Jetson/B210 validation with approved custom mounting                                                  |
| DJI Matrice 400          |                            6 kg payload, 59 min headline flight time |                      DJI store shows 13,035$ combo, resellers vary | A, B, C, D yes                                    | Safest full-payload recommendation                                                                                             |
| Freefly Astro Max        |                                                         3 kg payload |                                            USD 22,995$ store price | A and B yes, C no under 70% rule                  | More expensive than M350 and not enough margin for C                                                                           |

Sources checked on July 8, 2026:

| Source | Use |
| --- | --- |
| https://enterprise.dji.com/matrice-400 | Matrice 400 payload and flight-time reference |
| https://store.dji.com/product/dji-matrice-400-worry-free-plus-combo | Matrice 400 combo price reference |
| https://advexure.com/products/dji-matrice-350-rtk | Matrice 350 RTK reseller price and payload reference |
| https://enterprise.dji.com/matrice-350-rtk/specs | Matrice 350 RTK damper payload caution |
| https://store.freeflysystems.com/products/astro-max | Astro Max price reference |
| https://freeflysystems.com/astro/specs | Astro Max payload reference |
| https://www.flyingtech.co.uk/product/tarot-x8-lite-1050mm-foldable-octocopter-frame/ | Tarot X8-Lite frame price and load-time reference |
| https://alpha-rc-heli.com/shop/tarot-drone-x8-octocopter-kit-and-power-package/ | Tarot X8 all-up-weight power-package reference |

---

## Budget-friendly recommendation

| Priority | Path | Reason |
| --- | --- | --- |
| 1 | Configuration B on Matrice 350 RTK with custom mount approval | Cheapest vendor-supported validation path if Jetson throughput stabilizes after phone service |
| 2 | Configuration B on Tarot X8 prototype | Cheapest experimental path for local dummy-payload and tethered tests, but not turnkey |
| 3 | Configuration C on Matrice 400 | Best serious current-hardware path with real margin |
| 4 | Configuration D on Matrice 400 or heavier | Only if dual-radio or instrumentation becomes mandatory |

The more budget-friendly solution is therefore not to force the full mini-PC payload onto a smaller drone. It is to reduce the first airborne payload to Jetson-class compute, keep the B210 radio, and validate the architecture before buying the 6 kg-class platform.

For professor-facing planning, the recommendation is:

```yaml
procurement_strategy:
  first_step: Jetson + B210 + Quectel validation payload
  cheapest_vendor_path: Matrice 350 RTK only if custom mount is approved
  cheapest_lab_path: Tarot X8 prototype for non-production dummy-load testing
  full_system_path: Matrice 400 for mini-PC payload or dual-radio payload
  do_not_buy_yet: heavier platforms unless endurance or instrumentation requirements grow
```

---

## Current limits and risks

| Risk | Current handling |
| --- | --- |
| X310 106 PRB blocked by transport | Prove 10 GbE before another wide-band X310 run |
| X310 51 PRB still stops before attach | Focus on Msg3/random-access evidence, not core/F1 |
| Jetson machine-side success is not final service | Phone service now works, but throughput still needs stabilization |
| Jetson throughput below Pi/MiniPC | Focus on overflows, RTT spikes, scheduler evidence, and active NIC path |
| B205mini-i not validated | Keep as future lightweight branch only |
| Payload mass still estimated | Weigh the assembled payload before procurement |
| Performance-mode power unmeasured | Measure OAI DU power under B210 and Quectel traffic |
| Budget drone safety unknown | Treat Tarot builds as lab prototypes, not field-ready enterprise aircraft |
| Regulations and permissions | Check local flight approval, payload rules, and spectrum authorization |

---

## Next Steps

1. Close the X310 transport question: install or verify a real 10 GbE path before repeating 106 PRB.
2. Continue the X310 51 PRB path only with Msg3-focused evidence: random access, PRACH, timing advance, and UE attach logs.
3. Stabilize Jetson throughput: collect synchronized phone speed-test windows with MCS, BLER, LCID byte deltas, overflows, RTT, and UE context events.
4. Compare Jetson against Pi and MiniPC runtime settings: MCS floors, BLER targets, PUCCH and PUSCH targets, MSS clamping, CPU affinity, and IRQ placement.
5. Decide the Jetson Ethernet path: either cable and configure the ASIX USB Ethernet adapter for F1, or document that current Jetson F1 uses the integrated 1 GbE NIC.
6. Weigh the exact Jetson+B210+Quectel payload: include antennas, coax, DC converters, heatsink, enclosure, and mounting hardware.
7. Measure real power under OAI load: record DU runtime power during B210 operation and Quectel data activity.
8. Build a dummy payload at the Configuration B mass: test mounting, cooling, vibration, and center of gravity before flying electronics.
9. Ask vendors for two quotes: Matrice 350 RTK custom-mount validation package and Matrice 400 full-payload package.
10. Keep the B205mini-i branch separate: promote it only after attach, PWS/SIB8, user-plane traffic, and rollback evidence.
