## **Research Progress Report**  
Hardware Bottleneck Analysis & Migration Strategy

---

**Timeline:** April 7 - July 31, 2025 (16 weeks)

| Phase                | Weeks | Description                  |
| -------------------- | ----- | ---------------------------- |
| Planning/setup       | 1-2   | SOTA + Emulation             |
| Implementation       | 3-8   | OAI deployment, CU/DU        |
| Testing & Validation | 9-12  | Benchmarking/troubleshooting  |
| Documentation        | 13-16 | Results analysis             |

---

#### Issue 1: Instruction Set Architecture Mismatch

- OAI PHY layer uses x86 AVX-512 vector instructions for LDPC/Polar decoding
- Translation overhead: 40-60% performance loss

**Result:** x86 i7 is ~4-5x faster per core for 5G PHY workloads

---

#### Issue 2: USB Power management problem

![USB Power](graph2_usb_power_comparison.png)

The Jetson's tegra-xusb controller enters SC7 low-power state on 2-5ms throughput variations, causing VBUS droop that starves the USRP B210's FX3 controller. Result: `UHD rx8 transfer status: 5` — unrecoverable fatal error.

---

# Issue 3: DMA Bandwidth Saturation

![Bandwidth](graph1_bandwidth_comparison.png)

| Platform | Measured Throughput | Max Channel Width |
|----------|---------------------|------------------|
| Theoretical (USB 3.2 Gen 2) | 10 Gbps | 100 MHz |
| x86 Mini-PC (typical) | 5-8 Gbps | 80-100 MHz |
| Jetson Orin Nano | ~3 Gbps | <40 MHz |
| 5G NR Minimum (n78/n79) | ~4.5 Gbps | 50 MHz required |

**Jetson achieves only 30% of USB 3.2 theoretical bandwidth — non-compliant with 5G NR.**


---

#### CPU Comparison: Jetson vs. x86 Mini-PC


![Benchmark](graph6_benchmark_comparison.png)

---

#### Summary: Evidence-Based Architectural Correction

**Three Fundamental Limitations (Not Software-Correctable):**

| Issue                        | Root Cause                       | Project Impact                     |
| ---------------------------- | -------------------------------- | ---------------------------------- |
| **Instruction Set Mismatch** | AVX-512 → ARM                    | 40-60% overhead                    |
| **USB Power Management**     | tegra-xusb SC7 autosuspend       | Fatal UHD rx8 status: 5 disconnect |
| **DMA Bandwidth Saturation** | ~3 Gbps ceiling (30% of USB 3.2) | <40 MHz max channel width          |

**Literature Validation:** All successful UABS prototypes (SkyCell, SkyRAN) use x86 Mini-PC.

---
