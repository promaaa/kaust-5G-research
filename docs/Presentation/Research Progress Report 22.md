
# Jetson 5G backhaul recovery and budget drone sizing

**Date:** July 16, 2026
**Timeline:** April 7 to July 31, 2026 (16 weeks)

---

## What changed since last update

1. Jetson Quectel throughput recovered: the Nothing Phone reached approximately `40 Mbps` with the Jetson access DU using Quectel 5G and WireGuard for F1 backhaul.
2. Jetson runtime was aligned with the successful configuration: the 106 PRB access DU used the full downlink MCS range with `DL_MAX_MCS=28`.
3. TUI reproducibility was improved: the Jetson Quectel profile now checks modem and WireGuard prerequisites and preserves the validated runtime settings.
4. Topology validation was strengthened: phone traffic must be attributed to the access DU rather than the donor cell before throughput is accepted.
5. Drone and battery sizing remains based on the lighter Jetson and Raspberry Pi payload options.


---

## Jetson CU/DU with Quectel backhaul

The Jetson split configuration recovered the previously observed high-throughput result. In the latest Nothing Phone speed test, the downlink reached approximately **40 Mbps** while the Jetson operated as the access DU and the Quectel modem provided the 5G/WireGuard F1 backhaul to the CU on `serber-firecell`.

| Metric | Result |
| --- | --- |
| DU host | Jetson Orin Nano |
| Access radio | USRP B210 |
| Radio profile | 106 PRB |
| F1 backhaul | Quectel 5G with WireGuard |
| Phone throughput | Approximately `40 Mbps` |
| Previous Jetson result | Approximately `7.3 Mbps` |
| Improvement | Approximately `5.5x` |
| Measurement status | User-confirmed Nothing Phone speed test |

```yaml
jetson_quectel_result:
  access_du: serber-jetson
  access_radio: USRP_B210
  bandwidth: 106_PRB
  f1_transport: Quectel_5G_WireGuard
  dl_max_mcs: 28
  phone_throughput: approximately_40_Mbps
  previous_throughput: approximately_7.3_Mbps
```

This result changes the Jetson conclusion. The board is no longer only a service-capable low-throughput candidate. It now demonstrates throughput close to the earlier successful Quectel baseline while retaining the lower mass and power advantages needed for an airborne DU.

---

## Budget drone solution

The lowest-cost flight branch is not to shrink the current full payload onto an undersized drone. The better budget solution is to reduce the first airborne payload:

| Component                                        |                 Planning value | Comment                                                                |
| ------------------------------------------------ | -----------------------------: | ---------------------------------------------------------------------- |
| Raspberry Pi 5 board                             |    46 g, 25.5 W design ceiling | Uses the official 5.1 V, 5 A class power budget                        |
| USRP B205mini-i                                  | 24 g, about 5 W planning value | Very light USB SDR, not yet validated as the lab access-radio baseline |
| Quectel kit or backhaul modem support            |     180 g, 12 W planning value | Keeps the wireless F1 backhaul concept                                 |
| Light RF, cooling, timing, and cabling allowance |                     180 g, 8 W | Covers small fans, RF cables, filters, and accessories                 |
| Light power and mount allowance                  |                          300 g | DC regulators, wiring, plate, isolation, and enclosure                 |
| Electronics battery                              |                          208 g | Auline V45 3000 mAh 4S, 14.8 V, 44.4 Wh class                          |

For a 20 minute electronics runtime target, the planning payload is:

| Payload                                   | Fixed mass | Design power | Selected electronics battery  | Total payload | Required drone rating |
| ----------------------------------------- | ---------: | -----------: | ----------------------------- | ------------: | --------------------: |
| Raspberry Pi 5 + B205mini-i + Quectel kit |      730 g |         50 W | Auline V45 4S 3000 mAh, 208 g |       0.94 kg |               1.34 kg |

### Calculation method and source

The calculation comes from the drone dimensioning model prepared in the previous payload-sizing work. It is not a full aircraft endurance model. It is a first-order electronics and payload-sizing model used to decide whether a payload belongs on a small experimental drone, a medium enterprise drone, or a 6 kg-class platform.

The battery part uses the standard constant-power energy relation:

$$
E=P\,t
$$

The report then adds practical derating because the payload battery cannot be treated as perfectly usable. The selected battery must cover the payload power, the mission duration, electrical reserve, DC/DC losses, and usable battery fraction:

$$
E_\mathrm{nom}(S)=
\frac{P_\mathrm{payload}(S)t_\mathrm{mission}r_\mathrm{reserve}}
{\eta_\mathrm{dc}u_\mathrm{battery}}
$$

For the Raspberry Pi 5 + B205mini-i payload:

```yaml
calculation_inputs:
  payload_power: 50_W
  mission_time: 20_min
  mission_time_hours: 0.333_h
  electrical_reserve_factor: 1.30
  dc_efficiency: 0.88
  usable_battery_fraction: 0.80
```

So the nominal battery energy requirement is:

$$
E_\mathrm{nom}=
\frac{50\times0.333\times1.30}{0.88\times0.80}
\approx31.1\ \mathrm{Wh}
$$

The selected Auline V45 4S battery is `44.4 Wh`, so it covers the `31.1 Wh` requirement with margin. Its current capacity is also far above the expected payload current:

$$
I=\frac{50}{14.8}\approx3.4\ \mathrm{A}
$$

The drone rating part is a lab margin rule, not a published universal UAV formula. The payload should use at most 70% of the advertised payload rating:

$$
C_\mathrm{required}=
\frac{m_\mathrm{payload}}{\gamma_\mathrm{payload}}
=
\frac{0.94}{0.70}
\approx1.34\ \mathrm{kg}
$$

This is why the light payload needs a drone advertised above about `1.34 kg` payload. The 70% rule leaves margin for mounting, cooling, vibration isolation, antenna separation, temperature, altitude, wiring, and small integration mistakes.

This means the Raspberry Pi 5 + B205mini-i branch can be tested first on a cheaper Tarot X8-class experimental drone or another drone with at least a `1.34 kg` advertised payload rating. The current mini-PC/B210 branch should not use that budget class because its required drone rating is `3.37 kg`, before any flight-test uncertainty.

---

## Drone budget options

Prices and specifications should be refreshed before purchase. The table below is a planning snapshot checked on July 8, 2026.

| Option                |                                                            Approximate budget | Payload fit                                                                                                 | Recommendation                                                |
| --------------------- | ----------------------------------------------------------------------------: | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Tarot X8 custom build |                     lowest, frame and power package class rather than turnkey | Fits the 0.94 kg Pi/B205mini payload on paper, because the advertised all-up-weight class leaves room above the 1.34 kg requirement | Best budget lab prototype for dummy-load and controlled tests |
| DJI Matrice 350 RTK   |                                    about $14k class in current combo listings | Fits the light Pi/B205mini payload and Jetson/B210 validation payload, but custom mounting must be approved | Vendor-supported middle option                                |
| DJI Matrice 400       | about $15k to $20k class in current public estimates, with 6 kg payload class | Fits light, Jetson/B210, mini-PC/B210, and dual-radio payloads                                              | Safest full-system purchase                                   |
| Freefly Astro Max     |                                                              about $23k class | Fits light payloads, but not the full mini-PC/B210 payload under the 70% rule                               | Not the cheapest path for this project                        |

The recommended budget sequence is:

1. Build a non-flight dummy payload at `0.94 kg`.
2. Validate Raspberry Pi 5 + B205mini-i on the bench with OAI attach, PWS/SIB8, PDU session, and traffic.
3. Use a Tarot X8-class custom build only for local controlled payload testing if the lab accepts the integration risk.
4. Buy or quote Matrice 400 only when the project is ready to fly the heavier validated payload or needs enterprise flight safety and support.

```yaml
budget_solution:
  first_flight_candidate: Raspberry_Pi_5_B205mini_i_light_payload
  target_payload_mass: 0.94_kg
  electronics_battery: Auline_V45_3000mAh_4S
  cheapest_test_path: Tarot_X8_class_custom_build
  safer_vendor_path: Matrice_350_RTK_for_light_payload_only
  full_system_path: Matrice_400
  do_not_do: buy_large_drone_before_B205mini_lab_validation
```

---

## Why this is different from the full payload

The light payload is attractive because it changes the drone class. It is below 1 kg including the electronics battery, so it can be tested with much cheaper hardware. However, it is not yet the safest technical baseline because the B205mini-i has not replaced the B210 in lab validation.

| Configuration | Payload mass | Required drone rating | Technical confidence | Budget meaning |
| --- | ---: | ---: | --- | --- |
| Pi 5 + B205mini-i + Quectel | 0.94 kg | 1.34 kg | Low to medium until B205mini validation | Cheapest flight branch |
| Jetson + B210 + Quectel | 1.59 kg | 2.27 kg | Medium to high, phone service and approximately 40 Mbps throughput demonstrated | Best validation bridge |
| Mini-PC + B210 + Quectel | 2.36 kg | 3.37 kg | Highest match to current lab architecture | Needs Matrice 400 class |
| Dual-radio or instrumentation | 3.01 kg | 4.30 kg | Future expansion | Needs Matrice 400 or heavier |

The budget conclusion is therefore conditional:

```yaml
if_goal_is_cheapest_first_airborne_proof:
  choose: Pi_5_B205mini_i_light_payload
  drone_class: 2_kg_payload_custom_or_vendor_platform
  blocker: validate_B205mini_i_in_lab

if_goal_is_most_reliable_current_OAI_payload:
  choose: mini_PC_B210_or_Jetson_B210
  drone_class: Matrice_400
  blocker: procurement_cost
```

---

## Sources for budget and sizing

| Source                                                                                                                      | Used for                                                      |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| DJI Matrice 400 official page: https://enterprise.dji.com/matrice-400                                                       | 6 kg payload class and 59 minute headline flight time         |
| DJI Matrice 350 RTK official page: https://enterprise.dji.com/matrice-350-rtk                                               | Matrice 350 platform and payload family                       |
| DJI comparison page: https://enterprise-insights.dji.com/blog/dji-matrice-400-vs.-m350-rtk-detailed-upgrade-overview        | 6 kg Matrice 400 versus 2.7 kg Matrice 350 payload comparison |
| E38 Survey Solutions Matrice 350 listing: https://e38surveysolutions.com/products/dji-matrice-350-rtk-worry-free-plus-combo | Current Matrice 350 combo price snapshot                      |
| UAV Coach Matrice 400 article: https://uavcoach.com/matrice-400/                                                            | Public Matrice 400 price estimate range                       |
| Freefly Astro Max store: https://store.freeflysystems.com/products/astro-max                                                | Astro Max price reference                                     |
| Tarot X8 power package: https://alpha-rc-heli.com/shop/tarot-drone-x8-octocopter-kit-and-power-package/                     | Budget custom-drone class and 10 kg all-up-weight reference   |


---

## Next Steps

1. Validate B205mini-i before flight: prove attach, PWS/SIB8, PDU session, user-plane traffic, and rollback.
2. Weigh the light payload: include Pi, B205mini-i, Quectel kit, electronics battery, DC converters, cables, antennas, fan, and mounting plate.
3. Bench-test the electronics battery: verify voltage regulation, current margin, thermal behavior, and safe shutdown.
4. Build a `0.94 kg` dummy payload: use it for mounting, vibration, cooling, and center-of-gravity checks.
5. Quote two drone paths: Tarot X8-class custom build for controlled lab testing, and Matrice 350 or Matrice 400 for safer vendor-supported flight.
6. Keep X310 off the drone path until the host-to-X310 transport is proven above 1 GbE.
7. Reproduce the Jetson result from a clean TUI launch: confirm phone attachment through the access DU, Quectel attachment through the donor cell, PWS, internet, and approximately `40 Mbps` throughput.
