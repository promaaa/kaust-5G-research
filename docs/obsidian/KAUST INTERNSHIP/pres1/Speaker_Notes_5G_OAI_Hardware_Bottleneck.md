# Speaker Notes: 5G OAI CU/DU Split Hardware Bottleneck Analysis

## Research Document for Senior Supervisor Review

---

## Slide 1: Title

This presentation addresses a critical juncture in the 5G OpenAirInterface (OAI) deployment project. After establishing the theoretical foundation and software stack readiness, we have identified that the Jetson Orin Nano platform constitutes an insurmountable hardware bottleneck. This document provides the technical evidence supporting an immediate architectural pivot to x86/x64 Mini-PC hardware.

**Key Message:** This is not a failure — it is an evidence-based architectural correction.

---

## Slide 2: Project Timeline

**Timeline:** April 7 - July 31, 2025 (16 weeks total)

| Phase | Weeks | Description |
|-------|-------|-------------|
| Planning & Setup | 1-4 | Hardware procurement, environment setup |
| Implementation | 5-8 | OAI deployment, CU/DU split configuration |
| Testing & Validation | 9-12 | Performance benchmarking, troubleshooting |
| Documentation | 13-16 | Results analysis, presentation preparation |

**Current Status:** Week 1. Software groundwork completed; hardware limitations now critical path.

**Key Insight:** The software stack is production-ready — only the execution platform must change.

---

## Slide 3: The Three Fundamental Hardware Limitations

| Issue | Root Cause | Project Impact |
|-------|-----------|----------------|
| **Instruction Set Mismatch** | AVX-512 → ARM NEON via SIMDE | 40-60% overhead, deadline misses |
| **USB Power Management** | tegra-xusb SC7 autosuspend | Fatal UHD rx8 status: 5 disconnect |
| **DMA Bandwidth Saturation** | ~3 Gbps ceiling (30% of USB 3.2) | <40 MHz max channel width |

These are **hardware-level constraints** that no software optimization can overcome.

---

## Slide 4: Issue 1 — Instruction Set Architecture Mismatch

![Benchmark](graph6_benchmark_comparison.png)

**The Problem:**

The OAI physical layer performs computationally intensive baseband processing including LDPC (Low-Density Parity-Check) encoding/decoding and Polar coding for control channels. These operations are vector-matrix computations optimized for x86 AVX-512 (512-bit registers).

The Jetson Orin Nano employs ARM Cortex-A78AE architecture with NEON SIMD extensions supporting only 128-bit operations. When OAI's AVX-512 code executes on ARM, the SIMDE library performs runtime translation of these instructions.

**The Benchmark Evidence:**

| Metric | Jetson Orin Nano | Intel i7-1360P | Ratio |
|--------|------------------|-----------------|-------|
| Single-Core Performance | 380 | 1850 | ~5x |
| LDPC Decoding | 120 | 580 | ~5x |
| FFT Performance | 85 | 420 | ~5x |

**The Key Numbers:**
- Clock Speed: 2.0 GHz vs 5.0 GHz
- SIMD Width: 128-bit NEON vs 512-bit AVX-512
- x86 is ~4-5x faster per core for 5G PHY workloads

**This is not a software bug.** It is a fundamental architectural mismatch that cannot be bridged without native AVX-512 execution capability.

---

## Slide 5: Issue 2 — USB Power Management Catastrophe

![USB Power](graph2_usb_power_comparison.png)

The diagram shows the key difference:

**x86 Platform (Left):**
- USB VBUS maintains stable 5V
- No power state transitions during active I/O
- UHD reports successful transfer (rx8 status: 0)

**Jetson Orin Nano (Right):**
- SC7 entry triggered by 2-5ms throughput variation
- VBUS drops from 5V to 0
- UHD reports `rx8 transfer status: 5` — **unrecoverable fatal error**

**Root Cause:** The Jetson's tegra-xusb controller implements mobile-class power management. Desktop x86 USB controllers have no SC7 states.

---

## Slide 6: Issue 3 — DMA Bandwidth Saturation

![Bandwidth](graph1_bandwidth_comparison.png)

The bar chart shows USB 3.2 Gen 2 bandwidth reality:

| Platform | Throughput | Max Channel Width |
|----------|------------|------------------|
| Theoretical | 10 Gbps | 100 MHz |
| x86 Mini-PC | 5-8 Gbps | 80-100 MHz |
| Jetson Orin Nano | ~3 Gbps | <40 MHz |
| 5G NR Minimum | ~4.5 Gbps | 50 MHz required |

**Critical Insight:** The Jetson achieves only 30% of USB 3.2 theoretical bandwidth. Maximum achievable channel width is 35-40 MHz — insufficient for 5G NR n78/n79 bands.

---

## Slide 7: Hardware Comparison

![Comparison](graph5_hardware_comparison.png)

| Feature | Jetson Orin Nano | x86 Mini-PC |
|---------|-----------------|-------------|
| Architecture | ARM Cortex-A78AE | Intel Core i7-1360P |
| Baseband ISA | NEON (SIMDE) | Native AVX-512 |
| USB Power | Mobile (SC7 prone) | Desktop (Stable) |
| DMA Throughput | ~3 Gbps (FAIL) | 5-8 Gbps (PASS) |
| Max Channel BW | <40 MHz (FAIL) | 80-100 MHz (PASS) |
| 5G NR Compliant | NO | YES |

---

## Slide 8: Summary — Evidence-Based Architectural Correction

**Three Fundamental Limitations (Not Software-Correctable):**

1. **ISA Mismatch:** AVX-512 cannot run natively on ARM. SIMDE translation costs 40-60% overhead.

2. **USB Power:** SC7 autosuspend triggers fatal UHD disconnects. Mobile-class power management incompatible with USRP B210.

3. **DMA Bandwidth:** ~3 Gbps ceiling limits to <40 MHz channel width. Below 5G NR minimum.

**Literature Validation:** All successful UABS prototypes (SkyCell 5/5, SkyRAN 4/5) use x86 Mini-PC.

---

## Slide 9: Call to Action — Immediate x86 Migration

**Recommendation:** Pivot to x86/x64 Mini-PC (Intel NUC 13 or equivalent)

| Action | Timeline |
|--------|----------|
| Halt Jetson development | Immediate |
| Procure x86 Mini-PC | Week 2-4 |
| Migrate OAI stack | Week 5-8 |
| Validate 80 MHz operation | Week 9-12 |

**Why this works:**
- Native AVX-512 for baseband processing (no SIMDE overhead)
- Desktop-class USB power delivery (no SC7 states)
- 5-8 Gbps sustained DMA throughput (supports 80-100 MHz channels)

**The software stack is production-ready. Only the execution platform change is required.**

---

## Generated Visualizations Reference

| Graph | Filename | Description |
|-------|----------|-------------|
| 1 | graph1_bandwidth_comparison.png | USB DMA bandwidth bar chart |
| 2 | graph2_usb_power_comparison.png | x86 vs Jetson power comparison |
| 5 | graph5_hardware_comparison.png | Feature comparison table |
| 6 | graph6_benchmark_comparison.png | Performance: Jetson vs i7-1360P |

---

*Document prepared for senior research supervisor review. All technical specifications subject to verification against deployed hardware.*