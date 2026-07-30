# Power, payload mass, and Jetson throughput validation

**Date:** July 13, 2026
**Timeline:** April 7 to July 31, 2026 (16 weeks)

## 1. Power Consumption

The previous software readings were not measurements of total payload power. The Raspberry Pi value of `5.53 W` was a one-time sum of internal PMIC rails, the Jetson value of `5.86 W` was an idle-board `VDD_IN` reading, and the MiniPC values represented CPU package power only. None included the complete compute host, SDR, Quectel modem, cooling, and DC conversion path.

The corrected estimate is built from component operating ranges. The current target is **Raspberry Pi 5 + USRP B210 + Quectel RM500Q-GL**.

| Component                       |        Expected operating draw         | Sizing allowance | Basis                                                                                                                                                                                                                                                              |
| :------------------------------ | :------------------------------------: | :--------------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Raspberry Pi 5 running OAI DU   |               8 to 12 W                |       12 W       | Raspberry Pi reports about 4 W typical bare-board active power and about 12 W under its highest CPU stress workloads. OAI keeps multiple CPU cores active, so the typical desktop value is too low.                                                                |
| Jetson Orin Nano running OAI DU |               15 to 25 W               |       25 W       | NVIDIA defines 15 W and 25 W power modes for the Orin Nano 8 GB.                                                                                                                                                                                                   |
| MiniPC running OAI DU           |               45 to 65 W               |       65 W       | Engineering range for the complete x86 host. This remains unverified until a measurement is made.                                                                                                                                                                  |
| USRP B205mini-i                 |                3 to 5 W                |       5 W        | USB-powered 1x1 SDR allowance.                                                                                                                                                                                                                                     |
| USRP B210                       |    2.5 to 3.2 W for 1x1 full duplex    |      4.1 W       | Ettus reports `2.508` to `3.168 W` for 1x1 full duplex and up to `4.11 W` for 2x2 MIMO, depending on sample rate.                                                                                                                                                  |
| Quectel RM500Q-GL kit           | 4 to 8 W estimated during data traffic |       12 W       | The module uses `3.7 V` nominal power. Quectel requires a supply with `3.0 A` continuous capability, equivalent to `11.1 W`, but its published table leaves n78 traffic current as TBD. The working range is therefore an engineering estimate, not a measurement. |

The estimated battery-side DC input is:

$$
P_\mathrm{DC}=
\frac{P_\mathrm{compute}+P_\mathrm{SDR}+P_\mathrm{modem}+P_\mathrm{aux}}
{\eta_\mathrm{DC}}
$$

where $\eta_\mathrm{DC}=0.88$ and $P_\mathrm{aux}$ covers the fan, USB hub, and small interface losses.

| Configuration             | Expected full DC input | Recommended sizing ceiling | Status                                                           |
| :------------------------ | :--------------------: | :------------------------: | :--------------------------------------------------------------- |
| Pi 5 + B205mini           |       15 to 22 W       |            25 W            | Lightweight future configuration, not the current radio baseline |
| Pi 5 + B205mini + Quectel |       20 to 32 W       |            35 W            | Estimated only                                                   |
| Pi 5 + B210               |       15 to 22 W       |            25 W            | B210 radio path validated                                        |
| Pi 5 + B210 + Quectel |     19 to 30 W     |          35 W          | Current target setup, full input power not yet measured          |
| Jetson + B210             |       23 to 37 W       |            40 W            | Depends on the selected NVIDIA power mode                        |
| Jetson + B210 + Quectel   |       28 to 46 W       |            50 W            | Estimated only                                                   |
| MiniPC + B210             |       59 to 84 W       |            85 W            | Complete-host measurement still required                         |
| MiniPC + B210 + Quectel   |       64 to 93 W       |           100 W            | Estimated only                                                   |

The correct planning value for the present Pi payload is therefore 35 W, while the most likely sustained range is approximately 19 to 30 W. The `5.53 W` PMIC result must not be reported as Pi payload consumption. A USB-C inline meter on the Pi supply and a second meter on any independently powered hub are still required to replace this estimate with a measured value.

Sources: [Raspberry Pi power documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply), [Raspberry Pi 5 peak-power discussion](https://www.raspberrypi.com/news/introducing-raspberry-pi-5/), [Ettus B200/B210 power table](https://kb.ettus.com/B200/B210/B200mini/B205mini/B206mini), [NVIDIA Jetson Orin Nano power modes](https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html), and [Quectel RM500Q-GL hardware design](https://forums.quectel.com/uploads/short-url/az7J9yWjD4QD1Q0B7aPfB7ZZImI.pdf).

---

## 2. Component Weights

| Component                       | Measured Weight (g) | Notes                                                                              |
| :------------------------------ | :-----------------: | :--------------------------------------------------------------------------------- |
| **Raspberry Pi 5** (Board only) |        46.0         | +50g with plastic case                                                             |
| **Jetson** (Board only)         |        151.4        |                                                                                    |
| **MiniPC** (Board only)         |         441         |                                                                                    |
| **USRP B210** (Board only)      |        217.3        | with antennas; +200g with the case                                                 |
| **USRP B205 mini** (Board only) |         65          | with antennas; +82g with the case                                                  |
| **Quectel Modem Kit**           |        288.7        | with antennas                                                                      |
| **Auline V45 4S battery**       |         208         | 14.8 V, 3 Ah, 44.4 Wh, 45 A; selected for Pi and Jetson                            |
| **Auline S70 Ultra 6S battery** |         429         | 22.2 V, 5 Ah, 111 Wh, 70 A; selected for MiniPC                                    |
| **Pololu D24V90F5 converter**   |          5          | 5 V, 9 A; selected for Pi, rounded from 4.8 g bare-board mass                      |
| **Jetson DC-DC converter**      |          0          | No converter: fused 4S feed to the 9 to 20 V carrier-board input                   |
| **MG Power MPD-S108 converter** |         143         | 19 V, 70 W convection or 100 W forced-air; MiniPC choice pending 19 V confirmation |
| **Cables & Connectors**         |        ~100         | Includes fused XT60 input, low-voltage cutoff, distribution, and load leads        |
| **Mounting Plate / Frame**      |        ~150         |                                                                                    |

For a 20-minute electronics mission, the nominal battery requirement is:

$$
E_\mathrm{battery}=P_\mathrm{DC}\left(\frac{20}{60}\right)\frac{1.30}{0.80}
$$

The `1.30` factor provides reserve and `0.80` limits planned discharge to 80% of nominal capacity.

| Compute option | DC sizing ceiling | Required energy | Selected battery | Nominal load current | Capacity margin |
| :--- | ---: | ---: | :--- | ---: | ---: |
| Pi 5 + B210 + Quectel | 35 W | 19.0 Wh | Auline V45, 44.4 Wh | 2.4 A at 14.8 V | 2.34x |
| Jetson + B210 + Quectel | 50 W | 27.1 Wh | Auline V45, 44.4 Wh | 3.4 A at 14.8 V | 1.64x |
| MiniPC + B210 + Quectel | 100 W | 54.2 Wh | Auline S70 Ultra, 111 Wh | 4.5 A at 22.2 V | 2.05x |

The Pi converter output must be split between the Pi USB-C input and a separately fused powered USB hub for the B210 and Quectel modem. The Pi USB ports alone must not be treated as the power source for both devices. The Pololu converter must also pass a continuous 35 W bench test with flight-representative cooling. The Jetson 4S direct-feed choice is valid because the official carrier-board input accepts 9 to 20 V. The MiniPC converter choice is conditional until its required input voltage is confirmed as 19 V.

Sources: [Auline V45 battery](https://www.au-line.com/products/18650-v45-3000mah-4s1p-45a-xt60), [Auline S70 Ultra battery](https://morevolts.ca/auline-s70-ultra-5000mah-6s1p-22-2v-70a-battery-xt60/), [Pololu D24V90F5](https://www.pololu.com/product/2866), [Jetson Orin Nano carrier-board specification](https://developer.nvidia.com/downloads/assets/embedded/secure/jetson/orin_nano/docs/jetson_orin_nano_devkit_carrier_board_specification_sp.pdf), and [MG Power MPD-S108](https://www.mgpower.de/Official/resources/spec/MPD-S108.pdf).

---

## 3. Configuration Weights

The totals below include the selected battery and power-conversion hardware, the 100 g wiring allowance, and the 150 g mounting allowance. To optimize payload weight, **all cases are omitted** for the Pi 5, B205 mini, and B210 components.

| Configuration                   | Battery and power hardware | Target/Planning Weight (kg) | Measured Weight (g) *(No-Case)* |
| :------------------------------ | :------------------------- | :-------------------------: | :-----------------------------: |
| **Pi 5 + B205mini**             | V45 + Pololu, 213 g        |           0.94 kg           |           **574.0 g**           |
| **Pi 5 + B205mini + Quectel**   | V45 + Pololu, 213 g        |    1.04 kg (or 1.10 kg)     |           **862.7 g**           |
| **Jetson + B205mini**           | V45 + direct feed, 208 g   |    1.15 kg (or 1.07 kg)     |           **674.4 g**           |
| **Jetson + B205mini + Quectel** | V45 + direct feed, 208 g   |    1.25 kg (or 1.23 kg)     |           **963.1 g**           |
| **MiniPC + B205mini**           | S70 + MPD-S108, 572 g      |    2.28 kg (or 1.29 kg)     |          **1,328.0 g**          |
| **MiniPC + B205mini + Quectel** | S70 + MPD-S108, 572 g      |    2.38 kg (or 1.45 kg)     |          **1,616.7 g**          |
| **Pi 5 + B210**                 | V45 + Pololu, 213 g        |           1.48 kg           |           **726.3 g**           |
| **Pi 5 + B210 + Quectel**       | **V45 + Pololu, 213 g**    |         **1.58 kg *         |          **1,015.0 g**          |
| **Jetson + B210**               | V45 + direct feed, 208 g   |           1.69 kg           |           **826.7 g**           |
| **Jetson + B210 + Quectel**     | V45 + direct feed, 208 g   |           1.79 kg           |          **1,115.4 g**          |
| **MiniPC + B210**               | S70 + MPD-S108, 572 g      |           2.28 kg           |          **1,480.3 g**          |
| **MiniPC + B210 + Quectel**     | S70 + MPD-S108, 572 g      |          2.38 kg            |          **1,769.0 g**          |

The current Pi 5 + B210 + Quectel target configuration is therefore **1.015 kg (no case)**, which is significantly lighter than the target planning weight of 1.58 kg. These totals remain engineering estimates until the fully assembled payload is weighed on a single flight-representative scale.

---

## Jetson overflow solution

The overflow issue was solved by keeping the B210 on a real `5000M` SuperSpeed path and separating radio processing from USB interrupts. The DU runs on CPUs `1-5`, while the active B210 xHCI IRQ is pinned to CPU `0`. Performance mode, locked clocks, `usbfs_memory_mb=1000`, and warning-level OAI logging complete the runtime profile.

With this configuration, the Jetson CU/DU path remained stable and the Nothing Phone reached approximately 44 Mbps using Quectel 5G and WireGuard for F1 backhaul and 8 Mbps using Ethernet backhauling.

---

## All configuration validation

Jetson was added to the TUI for both 5G backhauling and Ethernet backhauling.
Every single configuration from the TUI was validated successfully.

---

## Next Steps

1. Finish the doc
2. Deploy on a real drone
3. Write a paper
