# End-to-end user-plane recovery and Pi 5 tuning

**Date:** May 17, 2026

**Timeline:** April 7 to July 31, 2026 (16 weeks)

---

## What changed since last update

1. CU/DU split with internet connectivity resolved: 5G bars + internet working after fixing radio downlink
2. Radio profile tuned: switched from 51 PRB (no RACH) to 106 PRB with `att_tx=3`, `att_rx=12`; full gain (`att_tx=0`) caused DL instability under load
3. Pi 5 system settings applied: USB current, CPU governor, no throttling
4. UPF shaping applied: `tbf rate 1500Kbit` on `tun0`
5. TUI updated: for live demos with cu/du

---

## Problem: 5G bars but no internet

The issue we had

| Direction | BLER | DTX | Result |
|---|---|---|---|
| Uplink (UE to gNB) | 0% | 2/7781 | Working fine |
| Downlink (gNB to UE) | 74% | 626 | MCS 0 pinned, no internet |

The data plane was verified correct end-to-end. The problem was purely in the radio downlink configuration, specifically TX/RX gain and PRB profile.

---

## Radio Profile Fix

Systematic testing identified the working configuration:

| Profile                           | Result                             |
| --------------------------------- | ---------------------------------- |
| 51 PRB                            | No RACH on Nothing Phone           |
| 106 PRB + full gain (`att_tx=0`)  | DL BLER climbed to 0.99 under load |
| 106 PRB + `att_tx=3`, `att_rx=12` | Stable: 5G bars + internet         |

Working RF parameters:

```yaml
prb: 106
absoluteFrequencySSB: 641280     # 3619.2 MHz
dl_absoluteFrequencyPointA: 640008
initialDLBWPlocationAndBandwidth: 28875
initialULBWPlocationAndBandwidth: 28875
controlResourceSetZero: 12
searchSpaceZero: 2
att_tx: 3
att_rx: 12
sdr_addrs: serial=35F8ABA
```

---

## Pi 5 System Settings

| Setting      | Value                                                     |
| ------------ | --------------------------------------------------------- |
| USB current  | `usb_max_current_enable=1` in `/boot/firmware/config.txt` |
| CPU governor | `performance` on cpu0-cpu3                                |
| Throttling   | `vcgencmd get_throttled = 0x0`                            |
Both CU and DU were using stale `2777` for F1-C and F1-U. Corrected to `2152`:

```
cu:
  f1c_ip: 10.76.170.38
  f1u_ip: 10.76.170.38
  f1c_port: 2152

pi:
  f1c_ip: 10.76.170.94
  f1u_ip: 10.76.170.94
  f1c_port: 2152
  remote_f1c_ip: 10.76.170.38
  remote_f1c_port: 2152
```

Pi only has one interface on the 10.76.170.0/25 subnet, so both F1-C and F1-U use `10.76.170.94`.

---

## TUI for live

The 5G TUI has been updated to support  not only monolithic, but also CU/DU split deployment and live demonstration, to enable easy reproducibility across hardware configurations (serber-pi, serber-minipc).

---

## Performance Results

| Configuration      | Throughput |
| ------------------ | ---------- |
| serber-pi (DU)     | 1.0 Mbps   |
| serber-minipc (DU) | 1.1 Mbps   |

Bottleneck unknown. serber-minipc previously achieved 40+ Mbps in monolithic mode with older antennas. Running only the DU on serber-minipc should give better results. The limitation may be in the F1 transport path or CU processing overhead, not the DU/RF.

---

## Current Setup

| Machine         | Role      |
| --------------- | --------- |
| serber-firecell | CU + Core |
| serber-minipc   | DU        |
| serber-pi       | DU        |

---

## Next Steps

1. Optimize current setup: investigate throughput bottleneck (2.2 Mbps on minipc vs 40 Mbps monolithic)
2. 5G backhauling: replace ethernet link between CU and DU with 5G connection
