# Downlink BLER adaptation, USRP X310 migration, and Jetson Orin Nano DU integration

**Date:** July 2, 2026
**Timeline:** April 7 to July 31, 2026 (16 weeks)

---

## What changed since last update

1. Downlink BLER bottlenecks root cause discovered.
2. USRP X310 access-cell migration evaluated: verified F1-C association and SIB8 path scheduling, but the required streaming bandwidth exceeded the 1 Gbps Ethernet transport limit, showing the need for a 10 Gbps path.
3. Jetson Orin Nano platform integrated: built custom SCTP-enabled kernel and compiled OAI natively under board memory limits.
4. Jetson DU F1-C and F1-U validated: established heartbeats with CU, corrected F1-U UDP port mapping, and verified user-plane ping connectivity to the UE IP.
5. B210 USB transport fixed: resolved USB 2.0 speed limit by using USB-C port to enable stable 106 PRB operation at USB 3.0 speed.
6. PWS broadcast validated on Jetson DU: rebuilt DU with the SIB8 patch, confirming successful reception of warning messages on the handset.

---

## Downlink BLER analysis and mitigation

The untuned Ethernet CU/DU split mode experienced a persistent Downlink Block Error Rate (BLER) of 22% to 35% under load. This high error rate resulted from the combination of GTP-U encapsulation overhead and the Transport Block size effect on the physical radio channel.

When user plane traffic is routed over the F1 interface, each IP packet is encapsulated in a GTP-U tunnel, which adds 40 to 50 bytes of header overhead. In a standard network with a path MTU of 1500 bytes, this encapsulation forces IP packets to exceed the MTU, causing fragmentation. Fragmented packets suffer from increased drop rates, raising the overall BLER.

To prevent fragmentation, the path MTU was raised to 9000 bytes. However, this exposed the Transport Block size effect. Without TCP MSS clamping, the TCP stack negotiated a large Maximum Segment Size based on the jumbo frame MTU. The gNB MAC layer scheduled these large segments into very large Transport Blocks on the physical radio channel (up to 14 KB at MCS 5).

In physical wireless transmission, the probability of block corruption increases with block length. Since HARQ operates on the entire Transport Block, a single bit error causes the entire block to fail its CRC check and trigger a NACK. This inflated the real radio BLER to 22% to 35%, well above the OAI default scheduler increment threshold.

--- 

### Setups comparison

The monolithic configuration bypasses GTP-U encapsulation and avoids transport MTU constraints. The physical layer Transport Blocks remain smaller, resulting in a low radio BLER. 

| Mode | F1 interface | TCP MSS clamping | Typical BLER | Dominant MCS | Throughput |
| --- | --- | --- | --- | --- | --- |
| Monolithic | absent | not required | below 5% | 18 to 21 | 150 to 190 Mbps |
| Split (untuned) | direct GbE | none | 22% to 35% | 5 | 12 to 22 Mbps |
| Split (tuned) | direct GbE | MSS 1360 | around 22% | 24 to 27 | 100 Mbps peak |

### Host and transport path benchmarks

The table below shows the measured handset throughput (or operational status) for each F1 transport configuration across the different DU candidate hosts in the lab.

| Configuration            | serber-firecell | serber-minipc | serber-pi | serber-jetson |
| ------------------------ | --------------- | ------------- | --------- | ------------- |
| Monolithic               | 150 to 190 Mbps | 150 Mbps      | 23 Mbps   | not tested    |
| Ethernet split (untuned) | not applicable  | 22 Mbps       | 2.3 Mbps  | 1.1 Mbps      |
| Ethernet split (tuned)   | not applicable  | 89 Mbps       | 21 Mbps   | 7.3 Mbps      |
| Quectel split (5G)       | not applicable  | 42 to 50 Mbps | 48 Mbps   | not tested    |
| Wi-Fi GRE split          | not applicable  | 52 Mbps       | 13 Mbps   | not tested    |

---

## Access-cell migration to USRP X310

| Component      | Value             |
| -------------- | ----------------- |
| Access radio   | USRP X310         |
| Link speed     | 1 GbE             |
| CU/core host   | `serber-firecell` |
| DU/radio host  | `serber-minipc`   |
| F1 transport   | Ethernet          |

### X310 bandwidth results

- **106 PRB result**: The DU reached F1/PWS/RF-ready state, but the X310 stream failed immediately with receive overflows (`ERROR_CODE_OVERFLOW`). Reducing the sample rate to `46.08 MSps` using the `-E` flag (requiring about 1.47 Gbps of raw transport throughput) also failed with overflows and RFNoC timeouts (`OpTimeout`). The fundamental bottleneck is the 1 Gbps Ethernet connection between the MiniPC and the USRP X310. Because the required streaming bandwidth exceeds the physical interface speed, a 10 Gbps Ethernet NIC and host path are required to support a 106 PRB configuration.


---

## Jetson Orin Nano DU integration

### Kernel compilation challenges

Enabling SCTP support on the Jetson Orin Nano required compiling a custom kernel. We encountered several difficulties across multiple attempts:

1. **Board Support Package source matching**: Initial compilation attempts using generic kernel sources failed because the Jetson Orin Nano requires the exact NVIDIA L4T BSP source code matching the running OS release (`R36.4.4` / JetPack 6.2).
2. **Proprietary out-of-tree drivers**: The Jetson BSP relies on out-of-tree drivers (including `nvgpu`, display controller, audio). Compiling only the main kernel source led to a bootable kernel but a broken system state where the display manager crashed and GPU acceleration was unavailable.
3. **Module symbol conflicts**: The out-of-tree modules must be compiled against the exact same kernel headers. Mismatched kernel versions or a missing `CONFIG_LOCALVERSION` configuration caused symbol mismatch errors on boot.
4. **Native build memory bottlenecks**: To avoid cross-compiling toolchain mismatches, we compiled natively on the Jetson board. This frequently crashed due to RAM exhaustion (8GB limit), which was resolved by creating a temporary swap space and constraining compiler parallelization with `make -j4`.
5. **Safe dual-boot recovery path**: A custom `initrd` and boot entry in `/boot/extlinux/extlinux.conf` were configured to allow fallback booting into the default stock kernel via a serial console.

### Jetson configuration and runtime tuning

| Setting | State |
| --- | --- |
| Jetson power mode | `MAXN_SUPER` |
| `jetson_clocks` | enabled |
| CPU governors | `performance` |
| CPU idle states | disabled |
| USB autosuspend | disabled |
| `usbfs_memory_mb` | `1000` |
| B210 USB speed | `5000M` |
| DU CPU affinity | CPUs `1-5` |
| USB IRQ affinity | CPU `0` |

### USB link-speed fix

The B210 initially enumerated on the Jetson as a USB 2.0 device at `480M` speed, which caused continuous UHD receive overflows (`ERROR_CODE_OVERFLOW`) at the `46.08 MSps` streaming rate. The issue was resolved by connecting the B210 via a USB 3.0 hub to the Jetson USB-C port, allowing it to correctly operate at `5000M` speed.

### User-plane and PWS validation

- **F1-C & F1-U Ok**: Confirmed by packet capture between the Jetson DU and the CU.
- **SIB8 PWS warning**: Rebuilt the DU binary with the SIB8/PWS patch to handle procedure code `20` (`F1AP_WRITE_REPLACE_WARNING`).
- **Internet Ok**: Connection verified but no speedtest

---

## Next steps

1. Benchmark all the configurations on the serber-jetson
2. Dimension the drone/battery according to the current chosen config
3. Doc


Now that everything is done, I would like to dimension the actual configuration of what we need for each real drone implementation: battery, usrp mini, quectel board, than that gives us the weight, and we know which drone to pick. I want you to actually implement mathematic formulas so we can easily change the configuration, based on the pc, or what we want to embark and propose several drones depending on the configuration we want to use.
