
# Drone-carried DU payload dimensioning and platform selection

**Date:** July 7, 2026
**Timeline:** April 7 to July 31, 2025 (16 weeks)

---

## What changed since last update

1. Drone payload sizing was formalized: the airborne DU concept is now expressed as a configurable mass, power, battery, and drone-selection model.
2. Formula provenance was added: the battery and endurance assumptions are now tied to published UAV endurance literature rather than being presented as unexplained calculations.
3. Four payload configurations were compared: a minimum USRP-mini proof, a Jetson plus B210 validation payload, an actual mini-PC plus B210 payload, and a heavier dual-radio prototype.
4. The current B210 baseline was preserved: the USRP B210 remains the validated access-radio reference, while the USRP B205mini-i is treated only as a lighter future candidate.
5. Drone choices were narrowed: Matrice 400 is the best first serious platform for the actual mini-PC plus B210 plus Quectel configuration, while Matrice 350 RTK and Freefly Astro Max are only comfortable for lighter profiles.
6. Power values were corrected for performance-mode procurement sizing: the model now uses design ceilings for Pi, Jetson, mini-PC, B210, B205mini-i, Quectel, RF/timing, and dual-radio allowances instead of optimistic typical values.
7. Real payload battery references were added: the model now selects concrete battery packs by Wh, current rating, and weight instead of inventing battery mass from a generic Wh/kg value.
8. Cost was corrected to match the actual procurement question: the budget table now reports drone price only, because the lab already has or can separately source the payload electronics.
9. Flight time was re-estimated with the corrected battery masses: each configuration now has an ideal Matrice 400 flight-time estimate and a planning estimate with 25% reserve.
10. A reusable calculator was implemented: `scripts/drone-du-sizing.py` recomputes the mass, real battery choice, required payload rating, drone fit table, drone-only cost table, and flight-time estimate from editable parameters.
11. A LaTeX dimensioning document was prepared: `docs/drone-du-dimensioning.tex` contains the detailed model and cited assumptions, although the local Tectonic installation currently fails before recompilation.
12. The USRP X310 migration was rechecked on `oai-pc`: the radio reached RF-ready state at 106 PRB, but the X310-facing link still negotiated at 1 GbE and failed with receive overflows, so the B210 remains the validated drone access-radio baseline.

---

## Motivation

The lab has now proven several important building blocks for a portable OAI DU: Ethernet CU/DU with SIB8 remains the rollback baseline, Wi-Fi and Quectel paths are under active validation, and the Jetson Orin Nano has shown that smaller hosts can run the DU role with a USRP B210 when the kernel, USB, CPU, and F1-U details are correct.

The next practical question is no longer only whether the radio stack can run. It is whether a real drone can carry the complete access-DU payload:

1. Compute board or mini-PC.
2. USRP access radio.
3. Quectel board and antennas for F1 backhaul.
4. Payload electronics battery.
5. RF cables, timing/GNSS, filters, enclosure, cooling, vibration isolation, mounting plate, and power conversion.

The goal of this report is to turn that packaging question into a mathematical model that can be changed easily. If the compute platform changes from Pi to Jetson to mini-PC, or if the radio changes from B210 to B205mini-i, the model should update the total weight and show which drone class is still realistic.

This is a design and procurement-sizing report. It does not claim that an airborne OAI DU has already flown or passed validation.

---

## Current architecture being dimensioned

The intended drone architecture keeps the lab split architecture:

| Element | Role |
| --- | --- |
| Ground 5GC and CU | Runs on `serber-firecell` |
| Donor DU | Provides the independent cell for the Quectel modem |
| Airborne access DU | Carries the local compute board, USRP access radio, and Quectel backhaul modem |
| Quectel modem | Provides wireless F1 backhaul from the airborne DU to the ground CU |
| Access radio | B210 remains the validated baseline radio |

The important design constraint is that the Quectel modem must attach to an independent donor cell. It must not depend on the same access cell that the drone DU is trying to backhaul. That would recreate the circular dependency already identified in the Quectel work:

```yaml
invalid_same_cell_loop:
  access_du_needs: F1 backhaul
  f1_backhaul_needs: Quectel PDU session
  quectel_pdu_needs: serving 5G cell
  invalid_case: Quectel attaches to the same access cell that requires F1
```

For drone dimensioning, the access DU payload therefore includes one access radio and one cellular backhaul modem. A future dual-radio prototype is also modeled, but it is treated as a heavier experimental case.

---

## Recent X310 transport result and drone-radio implication

The drone sizing model keeps the USRP B210 as the validated access-radio baseline. This is now more important after the latest USRP X310 migration attempt on `oai-pc`.

The X310 was moved away from the MiniPC to test whether a stronger host and Intel I225 Ethernet hardware could remove the 106 PRB bottleneck observed earlier. The expectation was that `oai-pc` might provide a better Ethernet path than the MiniPC, possibly through its 2.5 GbE-capable spare port.

The result was negative for 106 PRB. The test reached the X310 and reached RF-ready state, but the actual X310 path still behaved as a 1 GbE path and failed at the UHD receive stream. This means the problem persisted even after changing the Ethernet cable path and moving the radio host from `serber-minipc` to `oai-pc`.

### Tested X310 topology

| Element | Value |
| --- | --- |
| Candidate DU host | `oai-pc` |
| Management interface | `enp5s0` |
| Management IP | `10.76.170.24/25` |
| X310-facing interface | `enp3s0` |
| X310 IP | `192.168.10.3` |
| Access radio | USRP X310 |
| Intended bandwidth | 106 PRB |
| Reduced-rate mode | `-E`, `46.08 MSps` |
| Native mode | `61.44 MSps` |

The runtime-only X310 interface configuration was:

```yaml
oai_pc_x310_runtime:
  management_interface: enp5s0
  management_address: 10.76.170.24/25
  x310_interface: enp3s0
  x310_host_addresses:
    - 192.168.10.1/24
    - 192.168.20.1/24
    - 192.168.30.1/24
    - 192.168.40.1/24
  x310_radio_address: 192.168.10.3
  selected_mtu: 1500
  uhd_max_frame_size: 1472
```

### NIC and link result

`oai-pc` has the right class of Ethernet controller for a possible 2.5 GbE test, but the actual link did not negotiate at 2.5 GbE.

| Interface | Controller | Capability | Observed state |
| --- | --- | --- | --- |
| `enp0s31f6` | Intel I219-LM | 1 GbE | disconnected |
| `enp3s0` | Intel I225-V | 2.5 GbE capable | X310 path, negotiated 1 GbE |
| `enp5s0` | Intel I225-LM | 2.5 GbE capable | management, 1 GbE |
| `wlp0s20f3` | Intel Wi-Fi | Wi-Fi | disconnected |

The X310-facing port came up only at 1 GbE:

```yaml
enp3s0_observed:
  speed: 1000Mb/s
  duplex: full
  link_detected: true
  x310_ping: ok
  uhd_find_devices: ok
```

Forcing `2500baseT` did not solve it. It caused carrier loss:

```yaml
force_2500baseT_result:
  advertised_mode: 2500baseT/full
  negotiated_speed: unknown
  link_detected: false
  x310_ping: failed
  conclusion: current peer path does not accept 2.5 GbE
```

Jumbo MTU also failed. Setting MTU `8000` or `9000` caused the link to drop. The stable X310 path was only MTU `1500`, with UHD reporting a maximum frame size of `1472` bytes.

### Comparison with the previous X310 result

The new result should be read directly against the previous X310 work described earlier in this report series. The earlier MiniPC test already showed that 106 PRB was not stable on the X310 path. The purpose of moving to `oai-pc` and changing the Ethernet cable path was to test whether the limitation came from the MiniPC host, the old cable, or a weak physical connection.

The result shows that the failure persisted. The host changed, the X310 was connected through the spare `oai-pc` port, and UHD could discover the radio, but the negotiated link still stayed at 1 GbE and the radio stream still overflowed at 106 PRB.

| Test | Host | Cable or port change | Negotiated X310 link | OAI stage reached | Result |
| --- | --- | --- | --- | --- | --- |
| Previous X310 attempt | `serber-minipc` | MiniPC X310 Ethernet path | 1 GbE | RF-ready at 106 PRB | receive overflow and RFNoC timeout |
| New X310 attempt | `oai-pc` | X310 moved to `enp3s0` spare port | 1 GbE | RF-ready at 106 PRB | receive overflow and RFNoC timeout |

The important conclusion is that changing the Ethernet cable path did not remove the bottleneck. The evidence does not support a simple cable-fault explanation. The repeated pattern points to the available host-to-X310 Ethernet transport still being limited to 1 GbE, with no stable jumbo-frame or 2.5 GbE mode on this wiring.

In practical terms, this means the next X310 106 PRB attempt should not be another cable swap on the same 1 GbE-style path. It should start by proving the physical layer first:

```yaml
required_before_next_x310_106_prb_attempt:
  negotiated_link_speed: above_1GbE
  jumbo_mtu: stable
  uhd_frame_size: larger_than_1472
  uhd_streaming:
    - stable_46_08_MSps
    - stable_61_44_MSps_if_native_106_PRB_is_required
  f1_path:
    - DU_to_CU_reachability
    - SCTP_established
```

### F1 attempt

A temporary CU was started on `serber-firecell`, and an `oai-pc` DU was pointed at it. The CU reached the AMF and opened its F1 bindings:

```yaml
temporary_firecell_cu:
  oai_tree: /home/serber/cu-du-minipc-backhaul/source/openairinterface5g
  oai_commit: 9e67011af10f73264356366a59df7545349d9dab
  f1_c_bind: 10.76.170.38:38472
  f1_u_bind: 10.76.170.38:2153
  ng_setup_response: observed
```

The `oai-pc` DU attempted to use:

```yaml
temporary_oai_pc_du:
  oai_tree: /home/oai/sib8-spoofing
  oai_commit: 42128d314e7d3ca90b9bbaf91b3060f8cbebdf7b
  local_f1_address: 10.76.170.24
  remote_cu_address: 10.76.170.38
  x310_args: type=x300,addr=192.168.10.3,recv_frame_size=1472,send_frame_size=1472,otw=sc8
```

The split attempt did not reach radio activation because direct host-to-host traffic between `oai-pc` and `serber-firecell` failed:

| Check | Result |
| --- | --- |
| `oai-pc` to `serber-firecell` ping | failed |
| `serber-firecell` to `oai-pc` ping | failed |
| DU SCTP state | `COOKIE_WAIT` |
| CU F1 setup request from `oai-pc` | not observed |

Temporary `/32` gateway routes did not fix this. This means that a future split X310 test needs both a proven X310 radio link and a proven F1 path between the selected DU and CU hosts.

### Local radio transport result

To isolate radio transport from the blocked F1 path, local `--phy-test` runs were made on `oai-pc`.

The local `sib8-spoofing` tree crashed before UHD initialization in monolithic or local phy-test mode. The transport-only test therefore used the `cross-cell-verification` OAI tree:

```yaml
transport_test_oai:
  tree: /home/oai/cross-cell-verification
  commit: a39af6886a25ed26d88d3bca8cc9c3c0e043121f
  binary_banner: develop_a82077f4a0
  config_basis: gnb0.prs.band78.fr1.106PRB.usrpx310.conf
  mode: local_phy_test
  radio: USRP_X310
  radio_address: 192.168.10.3
  otw_format: sc8
```

The reduced-rate 106 PRB run with `-E` reached RF-ready state:

```yaml
result_106_prb_E:
  selected_sample_rate: 46080000
  actual_rx_sample_rate: 46.080000MSps
  actual_tx_sample_rate: 46.080000MSps
  radio_detected: X310
  radio_state: RU_0_rf_device_ready
  failure:
    - ERROR_CODE_OVERFLOW
    - problem_receiving_samples
    - RfnocError_OpTimeout
```

A tuned rerun with larger UHD queues and socket buffers reproduced the same failure:

```yaml
tuned_rerun:
  num_recv_frames: 4096
  num_send_frames: 4096
  recv_buff_size: 33554432
  send_buff_size: 33554432
  result: same_overflow_and_RFNoC_timeout
```

The native 106 PRB run reached `61.44 MSps` and then produced sustained receive overflows:

```yaml
result_106_prb_native:
  selected_sample_rate: 61440000
  actual_rx_sample_rate: 61.440000MSps
  actual_tx_sample_rate: 61.440000MSps
  radio_state: RU_0_rf_device_ready
  failure:
    - sustained_ERROR_CODE_OVERFLOW
    - problem_receiving_samples
    - RU_0_RF_device_stopped
```

### Interpretation for drone design

This result does not change the drone sizing recommendation toward the X310. It strengthens the reason to keep the B210 as the first airborne access-radio baseline.

| Question | Current answer |
| --- | --- |
| Can `oai-pc` drive X310 106 PRB on the current cable path? | No |
| Did `oai-pc` reach X310 RF-ready state? | Yes |
| Did 106 PRB remain stable after RF-ready? | No |
| Was the link actually 2.5 GbE? | No, it negotiated 1 GbE |
| Did jumbo MTU help? | No, it dropped the link |
| Was phone attach tested? | No, the system never reached a stable split access cell |
| Does this affect drone payload choice? | Yes, B210 remains the validated access radio |

The practical conclusion is:

```yaml
drone_radio_selection:
  validated_baseline: USRP_B210
  x310_status: transport_blocked_at_106_PRB
  x310_required_before_payload_model:
    - proven_high_speed_host_to_usrp_link
    - stable_UHD_streaming_at_target_sample_rate
    - stable_F1_path_between_DU_and_CU
    - phone_attach_and_PWS_validation
  current_payload_model_action: keep_X310_out_of_first_airborne_payload
```

This is also why the sizing model does not promote X310 as an airborne radio. The X310 is much larger, has a more demanding Ethernet transport path, and has not yet produced a phone-validated access cell in this lab. It remains a bench research branch, not the first drone payload radio.

---

## Formula model

The implemented sizing model separates payload electronics from the aircraft propulsion system. This is deliberate. At this stage, we need to know whether the radio and computing payload can fit within a drone class. We are not yet predicting exact flight time from rotor geometry, propeller efficiency, wind, or pilot profile.

For a selected payload configuration $S$, the model uses these variables:

| Symbol                    | Meaning                                                          |
| ------------------------- | ---------------------------------------------------------------- |
| $m_i$                     | Mass of component $i$, in grams                                  |
| $P_i$                     | Electrical power of component $i$, in watts                      |
| $x_i(S)$                  | 1 if component $i$ is included in configuration $S$, otherwise 0 |
| $t_\mathrm{mission}$      | Payload electronics runtime target                               |
| $r_\mathrm{reserve}$      | Electrical reserve multiplier                                    |
| $\eta_\mathrm{dc}$        | DC/DC conversion efficiency                                      |
| $u_\mathrm{battery}$      | Usable fraction of nominal battery capacity                      |
| $E_b$                     | Nominal energy of real candidate battery $b$, in Wh              |
| $I_b$                     | Continuous current rating of real candidate battery $b$, in A    |
| $V_b$                     | Nominal voltage of real candidate battery $b$, in V              |
| $m_b$                     | Mass of real candidate battery $b$, in grams                     |
| $\gamma_\mathrm{payload}$ | Maximum fraction of drone payload rating allowed for our payload |

The fixed payload mass is:

$$
m_\mathrm{fixed}(S)=\sum_i x_i(S)m_i
$$

The payload electrical power is:

$$
P_\mathrm{payload}(S)=\sum_i x_i(S)P_i
$$

The nominal payload battery energy is:

$$
E_\mathrm{nom}(S)=
\frac{P_\mathrm{payload}(S)t_\mathrm{mission}r_\mathrm{reserve}}
{\eta_\mathrm{dc}u_\mathrm{battery}}
$$

The selected payload electronics battery is now a real referenced battery pack, not an estimated material density:

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

The total payload mass is:

$$
m_\mathrm{payload}(S)=
m_\mathrm{fixed}(S)+m_{b^\*}
$$

The minimum drone payload rating is:

$$
C_\mathrm{required}(S)=
\frac{m_\mathrm{payload}(S)}{\gamma_\mathrm{payload}}
$$

The last equation is not a published UAV equation. It is a lab margin rule. With the current value $\gamma_\mathrm{payload}=0.70$, the payload should use no more than 70% of the advertised drone payload rating. This leaves margin for altitude, heat, battery aging, vibration isolation, mounting mistakes, antenna separation, and future small additions.

Flight time is estimated only for the selected drone class, not for the whole multirotor physics. For Matrice 400, the report uses three public planning points:

| Payload | Flight time |
| ---: | ---: |
| 0 kg | 59 min |
| 3 kg | 44 min |
| 6 kg | 31 min |

The flight time between two known payload points is linearly interpolated:

$$
T_\mathrm{ideal}(m)=
T_0+
\frac{m-m_0}{m_1-m_0}(T_1-T_0)
$$

A planning value is then computed with a reserve factor:

$$
T_\mathrm{planning}(m)=0.75T_\mathrm{ideal}(m)
$$

This reserve is not an aircraft manufacturer guarantee. It is a conservative lab planning allowance for takeoff, landing, wind, battery aging, temperature, regulatory reserve, and the difference between a published test condition and a real payload integration.

---

## Formula provenance

The payload battery equation is based on the constant-power energy budget $E=P\,t$, with additional derating for battery usable capacity and DC conversion losses. This is not a complete UAV endurance model, but it is a standard first-order electronics power budget.

The UAV literature supports this modeling choice as a first sizing layer:

| Source | What it contributes to this model |
| --- | --- |
| Hwang, Cha, and Jung, 2018, "Practical Endurance Estimation for Minimizing Energy Consumption of Multirotor Unmanned Aerial Vehicles" | Endurance is estimated from required power and battery discharge behavior, and payload weight is part of total vehicle weight. This supports using explicit power, battery, and payload variables. |
| Abdilla, Richards, and Burrow, 2015, "Power and Endurance Modelling of Battery-Powered Rotorcraft" | Battery-powered rotorcraft endurance depends on available battery capacity, usable capacity, and electric propulsion effects. This supports using a usable battery fraction instead of assuming the entire nominal pack capacity is available. |
| Zeng, Xu, and Zhang, 2019, "Energy Minimization for Wireless Communication with Rotary-Wing UAV" | Rotary-wing UAV energy has both propulsion and communication components. This supports separating payload electronics energy from the much larger drone propulsion energy instead of pretending the payload budget predicts total flight endurance. |

The most important boundary is that this report does not compute exact drone flight endurance. Exact endurance requires the aircraft manufacturer performance model or flight tests with the final payload because multirotor power depends on total weight, rotor geometry, propeller efficiency, air density, wind, and speed.

References:

| Reference | Link |
| --- | --- |
| Hwang, Cha, and Jung, Energies 2018 | https://www.mdpi.com/1996-1073/11/9/2221 |
| Abdilla, Richards, and Burrow, IROS 2015 | https://dl.acm.org/doi/10.1109/IROS.2015.7353445 |
| Zeng, Xu, and Zhang, IEEE TWC 2019 | https://arxiv.org/pdf/1804.02238 |
| DJI Matrice 400 flight-time and payload specification | https://enterprise.dji.com/matrice-400/specs |
| Sphere Drones Matrice 400 payload flight-time summary | https://www.spheredrones.com.au/resources/blog/dji-matrice-400-top-questions-answered-faq |

---

## Default sizing assumptions

The current parameters are intentionally conservative. They represent early procurement and bench-packaging assumptions, not final measured values.

```yaml
mission:
  payload_runtime_minutes: 20
  electrical_reserve_factor: 1.30
  usable_battery_fraction: 0.80
  dc_efficiency: 0.88
  max_payload_rating_utilization: 0.70
```

Interpretation:

1. The payload electronics battery is sized for 20 minutes of payload operation.
2. The energy demand is multiplied by 1.30 to keep reserve.
3. Only 80% of the nominal battery capacity is treated as usable.
4. DC conversion is assumed to be 88% efficient.
5. The battery is selected from real references only if nominal Wh and continuous current are both sufficient.
6. A drone is considered comfortable only if the computed payload is at most 70% of its advertised payload rating.

---

## Component assumptions

The model separates measured or vendor-published board weights from engineering allowances. For power, the table now uses performance-mode design ceilings for procurement sizing. These are deliberately not idle values. The purpose is to avoid buying a drone that only works for an optimistic bench number.

The DU should be run in performance mode during validation. On Jetson this means the Super/MAXN power profile and locked clocks. On x86 this means the CPU is allowed to boost under OAI load. The final value still has to be measured with the actual OAI DU, B210 sample rate, Quectel traffic, fan, SSD, and DC converters, but the procurement table should start from the power ceiling, not from a low average.

| Component                        |  Mass |     Power | Comment                                                                |
| -------------------------------- | ----: | --------: | ---------------------------------------------------------------------- |
| Raspberry Pi 5 board             |  46 g |    25.5 W | Uses the official 5.1 V, 5 A supply ceiling for Pi 5                   |
| Jetson Orin Nano carrier class   | 250 g |      35 W | 25 W Super/MAXN module mode plus carrier, fan, storage, and USB margin |
| Mini-PC x86 class                | 650 g |      65 W | Conservative performance-mode mini-PC budget under OAI load            |
| USRP B205mini-i                  |  24 g |       5 W | USB-powered SDR candidate, not yet the validated access-radio baseline |
| USRP B210                        | 350 g |       8 W | Current validated access-radio baseline with external-power margin     |
| Quectel RM500Q-GL kit            | 180 g |      12 W | Module supply design is sized around 3.7 V and 3 A peaks               |
| Light RF and timing allowance    | 180 g |       8 W | GNSS/timing, short RF cables, filters, small fans                      |
| B210 RF and timing allowance     | 250 g | 10 to 15 W | Heavier antenna separation, coax, filters, thermal margin              |
| Light power and mount allowance  | 300 g |  included | DC regulators, plate, isolation, wiring, enclosure                     |
| Medium power and mount allowance | 350 g |  included | B210 validation build                                                  |
| Heavy power and mount allowance  | 500 g |  included | x86 host, larger heatsink, serviceable enclosure                       |
| Dual-radio extra allowance       | 650 g |      45 W | Extra SDR, RF path, or field instrumentation                           |

Component reference notes:

| Item | Source |
| --- | --- |
| USRP B210 | Ettus/Digilent lists 97 x 155 x 15 mm and 350 g: https://digilent.com/shop/ni-ettus-usrp-b210-2x2-70mhz-6ghz-sdr-cognitive-radio/ |
| USRP B205mini-i | Ettus/Digi-Key datasheet lists 24.0 g and USB 3.0 bus power: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/822/6002-410-021_Web.pdf |
| USRP B2x0 power | Ettus documents B210 power around 1.9 W to 4.1 W depending on RX/TX channels and sample rate, and recommends external power for B210 MIMO or GPSDO: https://kb.ettus.com/B200/B210/B200mini/B205mini/B206mini |
| Quectel RM500Q-GL | Quectel/RS datasheet lists 30.0 x 52.0 x 2.3 mm and 8.7 g for the module: https://docs.rs-online.com/4d5d/A700000007974594.pdf |
| Quectel RM500Q-GL power design | Quectel hardware design says the module power source should provide at least 3.0 A and shows 3.7 V typical output with 3.0 A max load: https://the-wireless-haven-media.s3.us-east-2.amazonaws.com/wp-content/uploads/2021/07/13111322/Quectel_RM500Q-GL_Hardware_Design_V1.1.pdf |
| Jetson Orin Nano Super | NVIDIA documents the small edge developer kit and 25 W class Super mode: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/ |
| Jetson Super/MAXN mode | NVIDIA documents the Super performance mode and 7 W, 15 W, and 25 W module power options: https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/ |
| Raspberry Pi 5 power | Raspberry Pi lists the official Pi 5 supply at 5.1 V, 5 A, 25.5 W output: https://www.raspberrypi.com/products/27w-power-supply/ |
| Mini-PC x86 class power | ASUS NUC 13 Pro specifications list 40 W to 45 W cTDP CPU options, and ASUS support lists 120 W adapters for NUC13 i5/i7 models: https://www.asus.com/us/displays-desktops/nucs/nuc-mini-pcs/asus-nuc-13-pro/techspec/ and https://www.asus.com/support/faq/1052533/ |

The component references give the starting point, but final procurement should use measured mass and measured power of the actual assembled payload. The difference between a module and a flight-ready subsystem can easily dominate the module mass. The same is true for power: the B210 itself may draw only a few watts in a vendor table, but the airborne payload must include compute boost, Quectel transmit peaks, DC losses, fans, storage, and RF accessories.

---

## Computed payload configurations

The following table is the current output of the calculator using the default assumptions above.

| ID | Configuration | Fixed mass | Design power | Required energy | Selected battery | Battery mass | Payload mass | Required drone rating |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| A | Minimum proof: Pi 5, USRP B205mini-i, Quectel kit | 730 g | 50 W | 31.1 Wh | Auline V45 3000 mAh 4S 14.8 V Li-ion | 208 g | 0.94 kg | 1.34 kg |
| B | B210 validation: Jetson-class compute, USRP B210, Quectel kit | 1380 g | 65 W | 40.0 Wh | Auline V45 3000 mAh 4S 14.8 V Li-ion | 208 g | 1.59 kg | 2.27 kg |
| C | Actual mini-PC class: x86 mini-PC, USRP B210, Quectel kit | 1930 g | 100 W | 61.6 Wh | Auline S70 Ultra 5000 mAh 6S 22.2 V Li-ion | 429 g | 2.36 kg | 3.37 kg |
| D | Dual-radio prototype: mini-PC class plus extra RF margin | 2580 g | 145 W | 89.3 Wh | Auline S70 Ultra 5000 mAh 6S 22.2 V Li-ion | 429 g | 3.01 kg | 4.30 kg |

The main result is that the actual mini-PC plus B210 plus Quectel payload is not extremely heavy in absolute terms, but it is too heavy to treat as a small accessory. Once a conservative payload-rating margin is applied, it belongs on a 6 kg-class drone rather than on a 3 kg-class compact platform.

---

## Real battery references

The payload electronics battery is separate from the drone propulsion battery. The selected packs below are for the DU electronics, SDR, Quectel modem, fans, and DC conversion only. They are not replacing the aircraft flight batteries.

The model currently prefers Li-ion packs for the electronics payload because the required current is modest and steady. This gives better energy per gram than a high-discharge LiPo pack. A heavier Tattu LiPo is still listed as a fallback reference if procurement or safety review prefers a conventional high-discharge RC pack.

| Battery reference | Nominal energy | Continuous current | Weight | Used by | Source |
| --- | ---: | ---: | ---: | --- | --- |
| Auline V45 3000 mAh 4S1P 14.8 V Li-ion XT60 | 44.4 Wh | 45 A | 208 g | A, B | RaceDayQuads lists 3000 mAh, 14.8 V, 45 A, XT60, and 208 g: https://www.racedayquads.com/products/auline-18650-v45-4s-3000mah-14-8v-45a-li-ion-battery-xt60 |
| Auline S70 Ultra 5000 mAh 6S1P 22.2 V Li-ion XT60 | 111.0 Wh | 70 A | 429 g | C, D | More Volts lists 5000 mAh, 22.2 V, 70 A max, and 429 g: https://morevolts.ca/auline-s70-ultra-5000mah-6s1p-22-2v-70a-battery-xt60/ |
| Tattu G-Tech 5000 mAh 6S1P 22.2 V 45C LiPo XT60 | 111.0 Wh | 225 A class | 702 g | fallback | Foxtech lists 111 Wh, 6S1P, 45C, XT60, and 702 g: https://store.foxtech.com/g-tech-6s-5000mah-22-2v-45c-high-discharge-lipo-battery/ |

For the light configurations, the Auline V45 current margin is very large:

$$
I_A=\frac{50}{14.8}=3.4\ \mathrm{A}
$$

$$
I_B=\frac{65}{14.8}=4.4\ \mathrm{A}
$$

For the heavier configurations, the Auline S70 current margin is also large:

$$
I_C=\frac{100}{22.2}=4.5\ \mathrm{A}
$$

$$
I_D=\frac{145}{22.2}=6.5\ \mathrm{A}
$$

The current draw is far below the listed continuous current rating, so the battery choice is energy-limited, not current-limited. The important practical requirement is therefore safe integration: proper fusing, DC/DC regulation, strain relief, enclosure ventilation, fire-safe charging/storage, and a bench discharge test before flight.

---

## Drone selection matrix

The drone ratings below are planning gates based on public manufacturer specifications checked for this report. They are not flight approval. Payload capacity can decrease with altitude, temperature, battery state, propeller choice, gimbal connector, regional firmware limitations, and mounting interface.

| Drone | Planning payload gate | A | B | C | D | Interpretation |
| --- | ---: | --- | --- | --- | --- | --- |
| Freefly Astro Max | 3.0 kg | Fit | Fit | No | No | Good compact research platform only if the payload stays light |
| DJI Matrice 350 RTK | 2.7 kg gross-weight margin, but 960 g single gimbal damper limit | Fit | Fit | No | No | Possible for B only with a proper custom mount, not the small gimbal damper |
| DJI Matrice 400 | 6.0 kg | Fit | Fit | Fit | Fit | Best balanced first serious choice for mini-PC plus B210 plus Quectel |
| Inspired Flight IF1200A | 8.6 kg | Fit | Fit | Fit | Fit | Heavy-lift research choice when integration margin matters more than portability |
| Skyfront Perimeter 8 family | 10.0 kg maximum, 5.0 kg long-endurance class | Fit | Fit | Fit | Fit | Endurance-first platform, mechanically larger than needed for first proofs |

Drone source notes:

| Drone | Source note |
| --- | --- |
| Freefly Astro Max | Freefly documents 18 to 20 minutes at the 3 kg Astro Max payload point, and reseller pages list 3 kg payload capacity: https://freeflysystems.com/knowledge-base/how-long-can-astro-fly and https://www.dslrpros.com/products/freefly-astro-max |
| DJI Matrice 350 RTK | DJI lists 9.2 kg max takeoff weight, approximately 6.47 kg with two TB65 batteries, and 960 g max payload for the single gimbal damper: https://enterprise.dji.com/matrice-350-rtk/specs |
| DJI Matrice 400 | DJI lists up to 6 kg payload at the third gimbal connector under sea-level conditions: https://enterprise.dji.com/matrice-400/specs |
| Inspired Flight IF1200A | Inspired Flight documentation lists 8.6 kg max payload and 24.9 kg max gross takeoff weight: https://www.inspiredflight.com/if1200 |
| Skyfront Perimeter 8 family | Skyfront advertises a 5 kg payload for long endurance and 10 kg maximum payload for shorter duration: https://skyfront.com/ |

The Matrice 350 RTK requires special caution. Its gross takeoff margin suggests about 2.7 kg could be possible, but DJI also gives a much lower single-gimbal damper payload limit. Therefore, it should not be selected for a custom OAI payload unless the mounting interface is explicitly approved for the mass and vibration profile.

---

## Cost model

Cost matters because the project goal is not only to make an airborne DU technically possible. It is to keep the system reproducible and as cheap as possible while staying compatible with the validated lab architecture.

For this proposal, the budget field is deliberately drone-only. The lab already has, or can separately source, the compute boards, USRP radios, Quectel board, cables, and bench power hardware. The payload battery is listed by reference and weight because it affects drone sizing, but it is not added to the drone budget total.

The prices below were checked on July 7, 2026. They are budgetary procurement estimates, not purchase orders. Shipping, tax, import duty, educational discounts, spare propellers, mounting certification, payload insurance, and local vendor quotes can change the final number.

### Drone price assumptions

| Drone | Budget price | Source |
| --- | ---: | --- |
| DJI Matrice 400 | $10,400 | DSLRPros lists the Matrice 400 base drone at $10,400: https://www.dslrpros.com/collections/dji-matrice-400 |
| DJI Matrice 400 practical combo | $13,988 | DSLRPros lists a Matrice 400 bundle with BS100 battery station and TB100 battery at $13,988: https://www.dslrpros.com/collections/dji-matrice-400 |
| DJI Matrice 350 RTK | $11,500 | Vertex lists the Matrice 350 RTK at $11,500: https://store.vertexunmanned.com/products/matrice-350-rtk |
| Freefly Astro Max | $22,995 | DSLRPros lists the Freefly Astro Max Aircraft at $22,995: https://www.dslrpros.com/products/freefly-astro-max |
| Inspired Flight IF1200A | $32,000 | Inspired Flight shop lists IF1200 at $32,000: https://shop.inspiredflight.com/products/if1200a-heavy-lift |
| Skyfront Perimeter 8 | starts at $49,900 | Skyfront FAQ lists Perimeter 8 prices starting at $49,900: https://skyfront.com/perimeter-8 |

### Drone-only solution table

The table below uses the cheapest compatible listed drone by price. Because the Matrice 400 is both cheaper than the sourced Matrice 350 RTK and stronger than the compact platforms, it becomes the cheapest compatible listed drone for all four configurations.

| ID | Selected payload battery | Cheapest compatible listed drone | Drone-only budget | Ideal Matrice 400 flight | Planning Matrice 400 flight |
| --- | --- | --- | ---: | ---: | ---: |
| A | Auline V45 3000 mAh 4S, 208 g | DJI Matrice 400 | $10,400 | 54.3 min | 40.7 min |
| B | Auline V45 3000 mAh 4S, 208 g | DJI Matrice 400 | $10,400 | 51.1 min | 38.3 min |
| C | Auline S70 Ultra 5000 mAh 6S, 429 g | DJI Matrice 400 | $10,400 | 47.2 min | 35.4 min |
| D | Auline S70 Ultra 5000 mAh 6S, 429 g | DJI Matrice 400 | $10,400 | 44.0 min | 33.0 min |

If procurement wants the Matrice 400 bundle with the BS100 battery station and one TB100 flight battery, the drone-side budget becomes $13,988 for each configuration. This is still cheaper than the listed Freefly Astro Max and much more capable for Configurations C and D.

The cheapest realistic recommendation remains Configuration B or C on Matrice 400:

1. Configuration B is the safest first airborne validation target because it keeps the B210 radio baseline while replacing the mini-PC with Jetson-class compute.
2. Configuration C is the closest to the current mini-PC deployment and remains practical on Matrice 400, but it has less power and mass margin than B.
3. Configuration A is mechanically light but less validated because the B205mini-i is not yet the lab access-radio baseline.
4. Configuration D should only be selected if the dual-radio or instrumentation requirement is real, because it consumes more mass and power margin even though it still fits Matrice 400.

The flight-time estimates do not change the recommendation. Configuration B remains the best first airborne validation target because it gives an estimated 38.3 minutes of planning flight time on Matrice 400 while keeping the validated B210 radio. Configuration C remains the closest current-hardware packaging target, with an estimated 35.4 minutes of planning flight time.

---

## Interpretation by configuration

### Configuration A: minimum proof

Configuration A is the most attractive mechanically. It uses a Raspberry Pi 5, USRP B205mini-i, and Quectel kit. With performance-mode sizing, the computed payload is about 0.94 kg using the Auline V45 4S 3000 mAh pack, requiring a 1.34 kg drone payload rating under the 70% margin rule.

This configuration is useful if the goal is to prove the smallest possible airborne access-DU concept. However, it is not the safest first technical path because the B205mini-i is not yet the validated access-radio baseline for this lab. Before this becomes the main drone path, the lab must prove OAI attach, PWS/SIB8, user-plane traffic, and rollback using the B205mini-i.

### Configuration B: B210 validation payload

Configuration B keeps the USRP B210 and replaces the heavier mini-PC class with a Jetson-class compute platform. With Jetson performance-mode sizing, the computed payload is about 1.59 kg using the Auline V45 4S 3000 mAh pack, requiring a 2.27 kg drone payload rating.

This is the best validation bridge. It keeps the radio closest to the known working lab baseline while moving the compute into a more drone-compatible class. It can fit into the Matrice 350 RTK or Astro Max class on paper, but Matrice 400 is still more comfortable because it leaves room for antenna separation, enclosure growth, thermal design, and mistakes during the first integration.

### Configuration C: actual mini-PC class

Configuration C represents the most realistic first packaging of the current mini-PC style deployment. It includes x86 compute, the B210, the Quectel kit, and heavier mounting and thermal allowances. With a 100 W performance-mode design budget and the Auline S70 Ultra 6S 5000 mAh pack, the computed payload is about 2.36 kg, requiring a 3.37 kg drone payload rating.

This is where the compact-drone class stops being comfortable. A 3 kg-rated platform has almost no engineering margin after applying the 70% rule. The Matrice 400 is the best balanced platform for this configuration.

### Configuration D: dual-radio or instrumentation prototype

Configuration D adds 650 g and 45 W for a second RF path, extra SDR equipment, or field instrumentation. With the Auline S70 Ultra 6S 5000 mAh pack, the computed payload is about 3.01 kg, requiring a 4.30 kg drone payload rating.

This configuration should not start on a compact platform. It belongs on Matrice 400 or heavier from the beginning. IF1200A or Skyfront-class platforms become relevant if we decide that endurance, open integration space, or instrumentation margin matters more than portability.

---

## Recommended drone path

The recommended path is:

1. First airborne engineering target: Configuration B on Matrice 400.
2. Conservative current-hardware target: Configuration C on Matrice 400.
3. Minimum-weight research branch: Configuration A only after B205mini-i validation.
4. Heavy experimental branch: Configuration D on IF1200A or Skyfront only if dual-radio or long-endurance requirements become real.

The key recommendation is to avoid buying a drone that only fits the optimistic payload. The project history shows that the real system often needs extra RF margin, thermal fixes, USB or Ethernet adapters, and instrumentation. Matrice 400 gives enough room for that without immediately jumping to a much larger heavy-lift aircraft.

---

## Reproducible artifacts

The current dimensioning work is stored in the lab repository:

| Artifact | Purpose |
| --- | --- |
| `docs/drone-du-dimensioning.tex` | Detailed LaTeX model with formulas, assumptions, citations, and drone table |
| `docs/drone-du-dimensioning.pdf` | Existing compiled PDF from the first model pass |
| `scripts/drone-du-sizing.py` | Dependency-free calculator that recomputes the payload and drone fit table |

The calculator output can be reproduced with:

```yaml
command: python3 scripts/drone-du-sizing.py
verified_result:
  config_A_payload_kg: 0.94
  config_A_battery: Auline V45 3000 mAh 4S 14.8 V Li-ion
  config_A_drone_only_budget_usd: 10400
  config_A_planning_flight_min: 40.7
  config_B_payload_kg: 1.59
  config_B_battery: Auline V45 3000 mAh 4S 14.8 V Li-ion
  config_B_drone_only_budget_usd: 10400
  config_B_planning_flight_min: 38.3
  config_C_payload_kg: 2.36
  config_C_battery: Auline S70 Ultra 5000 mAh 6S 22.2 V Li-ion
  config_C_drone_only_budget_usd: 10400
  config_C_planning_flight_min: 35.4
  config_D_payload_kg: 3.01
  config_D_battery: Auline S70 Ultra 5000 mAh 6S 22.2 V Li-ion
  config_D_drone_only_budget_usd: 10400
  config_D_planning_flight_min: 33.0
```

The LaTeX source currently contains the same formulas and citations. The local Tectonic installation on the Mac currently fails before compilation with a runtime panic, so the source was updated but the PDF was not regenerated in the latest pass. The source remains suitable for Overleaf or another LaTeX environment.

---

## Current limits and risks

The model is useful for procurement and engineering planning, but it should not be overinterpreted.

| Risk                                         | Current handling                                                              |
| -------------------------------------------- | ----------------------------------------------------------------------------- |
| Exact flight time unknown                    | Not computed here. Must be validated with the selected drone and real payload |
| B205mini-i not validated                     | Treated as a future candidate only                                            |
| Quectel full F1 backhaul not stable baseline | Drone work remains a packaging step after packet-gated validation             |
| X310 106 PRB not transport-stable            | Keep X310 as a bench branch until a link above 1 GbE and stable UHD streaming are proven |
| Payload mass still partly estimated          | Final decision requires weighing the assembled payload with the selected battery |
| Performance-mode power still unmeasured      | Measure OAI DU power under CPU performance mode, B210 operation, and Quectel traffic |
| Thermal behavior unknown                     | Add thermal logging and heat-soak tests before flight                         |
| RF and antenna separation unknown            | Keep mass margin for standoffs, coax, filters, and shielding                  |
| Supplier prices can drift                    | Refresh all prices before procurement                                         |
| Regulations and permissions                  | Check local flight approval, payload rules, and spectrum authorization        |
| Flight-time estimate is simplified           | Validate with the vendor planner and a real payload hover or route test       |


The most important engineering risk is not the battery mass. The payload electronics battery is relatively small in the current 20 minute model. The bigger risk is integration mass: enclosure, mounting plate, thermal hardware, RF cabling, antennas, and adapters can grow quickly. This is why a 6 kg-class drone is recommended even when the computed electronics payload is only around 2.36 kg for the current mini-PC class.

---

## Next Steps

1. Weigh the exact physical payload: compute board, SDR, Quectel carrier, antennas, coax, DC converters, heatsink, enclosure, and mounting hardware.
2. Measure real power under OAI load: record DU runtime power during B210 operation and Quectel data activity, not idle board power.
3. Update the calculator: replace estimated masses and powers in `scripts/drone-du-sizing.py` with measured values.
4. Refresh drone supplier prices before procurement: base drone, battery station, flight batteries, spare propellers, mount, shipping, and import duty.
5. Validate flight time with the selected drone: compare the interpolation estimate against the vendor planner, then perform a real hover or route test with a dummy payload of the same mass.
6. Validate the light radio branch separately: only promote B205mini-i after attach, PWS/SIB8, user-plane traffic, and Ethernet rollback evidence.
7. Keep X310 out of the first drone payload: only reconsider it after a host-to-USRP link above 1 GbE, stable UHD streaming at 106 PRB, working F1 to the CU, phone attach, and PWS/SIB8 validation.
8. Select the first drone platform: use Matrice 400 as the first serious target unless procurement constraints force a lighter validation-only path.
9. Prepare a bench payload mockup: include the real mounting plate, antenna layout, cooling, and cable strain relief before flight.
10. Keep validation evidence sanitized: record OAI commit, payload mass, power profile, thermal state, Quectel state, F1-C/F1-U packet proof, phone service/PWS observation, and rollback status without committing secrets or raw captures.
