
# X310 transport, embedded DU benchmarks, and drone payload sizing

**Date:** July 8, 2026
**Timeline:** April 7 to July 31, 2026 (16 weeks)

---

## What changed since last update

1. X310: New cable installation and tests
2. Jetson throughput improved and limitations of the board
3. New tests on the Raspberry pi
4. Drone and battery sizing
5. Documentation

---

## X310: New cable installation and tests

Despite the new 40 Gb/s cable that we have received, the X310 106 PRB problem is still not solved. The cable itself is now no longer the main unknown, but the X310 link still behaves like a 1 GbE path in practice. The 106 PRB configuration therefore still produces UHD overflows and cannot reach a phone-visible validation point. We also tested the reduced `-E` mode at `46.08 MSps`, but it still overflowed after the radio reached RF-ready state. The native 106 PRB mode at `61.44 MSps` was even more demanding and also failed with sustained overflow behavior.

The important conclusion is that changing the cable did not remove the bottleneck. This result matches the earlier X310 tests: 106 PRB is blocked before attach by the host-to-radio transport path, not by the CU, core network, or PWS configuration. The next useful X310 test should start by proving a real high-speed negotiated link to the radio, with stable MTU and UHD streaming, before spending more time on OAI-side radio tuning.

---

## Jetson throughput improved and current limitations

We have managed to improve the throughput in Ethernet CU/DU split from 720 Kbit/s last week to 7.3 Mb/s this week. This is still a lot lower than serber-pi (23 Mb/s) and serber-minipc (89 Mb/s) with the same configuration.

To improve it we moved the Jetson into its maximum performance mode, enabled `jetson_clocks`, forced the CPU governors to `performance`, disabled USB autosuspend, increased `usbfs_memory_mb`, and pinned the DU process to CPUs `1-5` while leaving CPU `0` for USB and kernel work. We also corrected the F1-U path, verified that the B210 was running on the USB 3.0 tree at `5000M`. These changes moved the result from a barely usable connection to phone-visible PWS, 5G registration, internet access, and about `7.3 Mb/s`, but they did not remove the remaining overflow and BLER problem.

The remaining limitation is the USB bandwidth. Currently we have a USB-c hub plugged into the only USB 3.0 (type-c) port of the board to plug both the USRP B210 and the Quectel. The problem is that even with only the USRP B210 plugged into it we encounter overflow and thus very high BLER (+60%).

The next action is probably to buy a small USB-C -> USB-B cable to see if we can get it to work with just the USRP B210 in the first place, and then we can deploy other configs.


---
## New tests on the Raspberry Pi

I was surprised by the results I've got with the raspberry Pi last week so I took the time to run some new experiments and to adjust different parameters in the configuration. This ended up with a great improvement. Here is the updated table:

| Configuration            | serber-firecell | serber-minipc | serber-pi | serber-jetson |
| ------------------------ | --------------- | ------------- | --------- | ------------- |
| Monolithic               | 150 to 190 Mbps | 150 Mbps      | 23 Mbps   | not tested    |
| Ethernet split (untuned) | not applicable  | 22 Mbps       | 2.3 Mbps  | 1.1 Mbps      |
| Ethernet split (tuned)   | not applicable  | 89 Mbps       | 21 Mbps   | 7.3 Mbps      |
| Quectel split (5G)       | not applicable  | 42 to 50 Mbps | 48 Mbps   | not tested    |
| Wi-Fi GRE split          | not applicable  | 52 Mbps       | 13 Mbps   | not tested    |


---
## Drone and battery sizing


The sizing method follows the first-order battery/endurance logic used by **Hwang, Cha, and Jung, _Practical Endurance Estimation for Minimizing Energy Consumption of Multirotor Unmanned Aerial Vehicles_**: flight time is limited by required power, battery discharge, and payload weight. Here we use only the simplified electronics part of that idea: $E=P\,t$, then derate for DC efficiency, usable capacity, and reserve.

### Sizing assumptions

The payload battery sizing uses:

$$

E_\mathrm{nom}(S)=

\frac{P_\mathrm{payload}(S)t_\mathrm{mission}r_\mathrm{reserve}}

{\eta_\mathrm{dc}u_\mathrm{battery}}

$$
where:

| Symbol               | Meaning                                      |     Planning value |
| -------------------- | -------------------------------------------- | -----------------: |
| $P_\mathrm{payload}$ | electrical payload power in performance mode | scenario-dependent |
| $t_\mathrm{mission}$ | target powered mission duration              |   20 min = 0.333 h |
| $r_\mathrm{reserve}$ | reserve factor                               |               1.30 |
| $\eta_\mathrm{dc}$   | DC/DC conversion efficiency                  |               0.88 |
| $u_\mathrm{battery}$ | usable fraction of nominal battery energy    |               0.80 |

For example, for the Raspberry Pi 5 + B205mini-i payload:

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



### Configurations recap


Planning value = `payload mass`, `payload power`, `battery energy requirement`, and `required advertised drone payload rating`.



| Component                   |                          Planning value | Comment                                                                                                                                |
| --------------------------- | --------------------------------------: | -------------------------------------------------------------------------------------------------------------------------------------- |
| Pi 5 + B205mini             |  `0.94 kg`, `50 W`, `31.1 Wh`, `1.34kg` | Baseline light branch. One Auline V45 battery is enough for the 20 min powered payload target.                                         |
| Pi 5 + B205mini + Quectel   |  `1.04 kg`, `60 W`, `37.3 Wh`, `1.49kg` | Still compatible with a 2 kg advertised payload drone under the 70% lab rule.                                                          |
| Jetson + B205mini           |  `1.15 kg`, `60 W`, `37.3 Wh`, `1.64kg` | Uses Jetson performance mode planning, not average measured power. Still inside Tarot X8-Lite class.                                   |
| Jetson + B205mini + Quectel | `1.25 kg`, `70 W`, `43.5 Wh`, `1.79kg ` | Electrically close to one Auline V45 battery, but still acceptable on the nominal formula. Bench validation is required before flight. |
| Minipc + B205mini           |  `2.28 kg`, `85 W`, `52.9 Wh`, `3.26kg` | Not compatible with the budget 2 kg payload drone class. Needs a 5 kg-class heavy-lift platform.                                       |
| Minipc + B205mini + Quectel | `2.38 kg`, `95 W`, `59.1 Wh`, `3.40kg ` | Heaviest branch. Similar required rating to the existing mini-PC/B210 case, so it should skip the Tarot X8-class test platform.        |



The formulas give us:


| Component                   |                       Battery | Drone                                              | Approximate flight time | Price for Drone + Battery |
| --------------------------- | ----------------------------: | -------------------------------------------------- | ----------------------- | ------------------------- |
| Pi 5 + B205mini             | `1× Auline V45 4S`, `44.4 Wh` | Tarot X8-Lite RTF class, `2 kg` advertised payload | `≈29 min`               | `≈$1,447`                 |
| Pi 5 + B205mini + Quectel   | `1× Auline V45 4S`, `44.4 Wh` | Tarot X8-Lite RTF class, `2 kg` advertised payload | `≈28 min`               | `≈$1,447`                 |
| Jetson + B205mini           | `1× Auline V45 4S`, `44.4 Wh` | Tarot X8-Lite RTF class, `2 kg` advertised payload | `≈27 min`               | `≈$1,447`                 |
| Jetson + B205mini + Quectel | `1× Auline V45 4S`, `44.4 Wh` | Tarot X8-Lite RTF class, `2 kg` advertised payload | `≈27 min`               | `≈$1,447`                 |
| Minipc + B205mini           | `2× Auline V45 4S`, `88.8 Wh` | T-Drones M1200 class, `5 kg` advertised payload    | `≈60 min class`         | `≈$3,695+`                |
| Minipc + B205mini + Quectel | `2× Auline V45 4S`, `88.8 Wh` | T-Drones M1200 class, `5 kg` advertised payload    | `≈60 min class`         | `≈$3,695+`                |

Before any real flight, we should measure precisely the payload with:

```bash
actual_payload_mass_kg=<measured_value>
actual_payload_power_w=<measured_value_under_performance_mode>
actual_battery_voltage_v=<measured_value>
actual_runtime_min=<bench_runtime_until_safe_cutoff>
```

Then recompute:
$$

E_\mathrm{nom,measured}=

\frac{P_\mathrm{measured}\times0.333\times1.30}{0.88\times0.80}

$$and:

$$

C_\mathrm{required,measured}=\frac{m_\mathrm{measured}}{0.70}

$$

---

## Drone budget options

Prices and specifications should be refreshed before purchase. The table below is a planning snapshot checked on July 8, 2026.

| Option                | Approximate budget | Payload fit                                                                                                          | Recommendation                                                                        |
| --------------------- | -----------------: | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Tarot X8 custom build |         about $934 | Fits the 0.94 kg Pi/B210 payload on paper; not for the current mini-PC/B210 branch without a full build margin check | Best budget lab prototype for light-load and controlled tests                         |
| T-Drones M1200 class  |              $3,6k | Fits the 0.94 kg light payload and likely the 2.36 kg mini-PC/B210 payload                                           | Budget heavy-lift research platform if we are ready to accept custom integration risk |
| DJI Matrice 350 RTK   |              $9,4k | OK for all config up to the 2.36 kg mini-PC/B210 payload                                                             | Vendor-supported middle option                                                        |
| DJI Matrice 400       |              $9,5k | Fits light, Jetson/B210, mini-PC/B210, and dual-radio payloads with the best margin in this table                    | Safest full-system purchase                                                           |
| Freefly Astro Max     |               $23k | Fits light payloads, but not the full mini-PC/B210 payload under the 70% rule                                        | Not the cheapest path for this project                                                |

---

## Next Steps

1. Finish the doc
2. Weigh the light payload: include Pi, B205mini-i, Quectel kit, electronics battery, DC converters, cables, antennas, fan, and mounting plate.
3. Bench-test the electronics battery: verify voltage regulation, current margin, thermal behavior, and safe shutdown.
4. Build a `0.94 kg` dummy payload with the current drone from the lab
5. Deploy it for real
6. Keep X310 off the drone path until the host-to-X310 transport is proven above 1 GbE.
7. Continue Jetson optimization separately: it is service-capable now, but throughput still needs to approach the Pi and MiniPC baselines.
