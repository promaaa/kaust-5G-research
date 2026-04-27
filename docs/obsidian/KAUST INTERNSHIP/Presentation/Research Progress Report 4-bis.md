**Timeline:** April 7 – July 31, 2025 (16 weeks)

| Phase | Weeks | Description |
| --- | --- | --- |
| Planning/Setup | 1–2 | SOTA + Emulation |
| Implementation | 3–8 | OAI deployment, CU/DU |
| Testing & Validation | 9–12 | Benchmarking/troubleshooting |
| Documentation | 13–16 | Results analysis |

---

## What Changed Since Last Update

Major breakthrough: Raspberry Pi 5 can now sustain real-time 5G NR L1 processing at 24 PRB (10 MHz) without crashing. Previously, at 106 PRB (40 MHz), the Pi 5 crashed after just 2-3 seconds due to CPU overflow. This discovery makes the Pi 5 a viable DU candidate for demonstrating CU/DU split functionality.

---

## Recap: Previous Architecture

**Drone Vision (Goal):**

```mermaid
graph LR
    subgraph Drone["Drone"]
        A["DU + USRP B210<br>L1 + MAC + RF"]
    end
    subgraph Ground["Ground Station"]
        B["CU<br>L2 + L3 AMF + CN<br>Core Network"]
    end
    A -->|"F1 (??)"| B
    style A fill:#064e3b,stroke:#10b981,color:#fff
    style B fill:#064e3b,stroke:#10b981,color:#fff
```

**Full stack on serber-minipc (previously validated):**

```mermaid
graph LR
    subgraph serber-minipc["serber-minipc (Intel N95)"]
        A["DU + USRP B210<br>106 PRB, 61.44 MHz"]
    end
    subgraph serber-firecell["serber-firecell"]
        B["CU + AMF"]
    end
    A -->|"F1-C (SCTP)"| B
    style A fill:#064e3b,stroke:#10b981,color:#fff
    style B fill:#064e3b,stroke:#10b981,color:#fff
```

**Architecture: CU/DU Split with Pi 5**

```mermaid
graph LR
    subgraph serber-pi["serber-pi (Pi 5)"]
        A["DU<br>24 PRB (10 MHz)<br>L1 + MAC + RF"]
    end
    subgraph serber-firecell["serber-firecell"]
        B["CU + AMF + CN<br>Full 5G Stack"]
    end
    A -->|"F1-C (SCTP)"| B
    B -->|"N2 (SCTP)"| A
    style A fill:#064e3b,stroke:#10b981,color:#fff
    style B fill:#064e3b,stroke:#10b981,color:#fff
```



---

## The Problem: Pi 5 L1 Processing at Full Bandwidth

From previous testing, the Pi 5 crashed at 106 PRB:

```
ERROR_CODE_OVERFLOW (Overflow)
[PHY] rx_rf: Asked for 30720 samples, got 23547 from USRP
```

**Root cause:** Pi 5's Cortex-A76 cores cannot keep up with 5G NR baseband processing (FFT, channel estimation, equalization) at 106 PRB + 61.44 MHz sample rate.

---

## The Solution: Lower PRB Configuration

By reducing the bandwidth to 24 PRB (~10 MHz), we achieve:

| Metric         | 106 PRB (40 MHz) | 24 PRB (10 MHz) |
| -------------- | ---------------- | --------------- |
| Pi 5 L1 Status | CRASH after 2-3s | STABLE          |
| CPU Load       | 100%+ (overflow) | ~40-60%         |
| PRB Count      | 106              | 24              |
| Bandwidth      | 40 MHz           | 10 MHz          |
| Sample Rate    | 61.44 MHz        | ~15 MHz         |

---

## Testing: Pi 5 as DU with 24 PRB

I created a custom 24 PRB configuration for band n78 and tested on serber-pi (Pi 5).

### Configuration Created

```
gnb-du.sa.band78.24prb.usrpb210.conf
- Band: n78 (3.5 GHz)
- PRB: 24 (~10 MHz)
- SCS: 30 kHz
- DL frequency: 3604.8 MHz
- CORESET index: 2
```

### Key Parameters Discovered

| Parameter | Value | Notes |
| --- | --- | --- |
| CORESET index | 2 | Must use `initialDLBWPcontrolResourceSetZero = 2` for 24 PRB |
| SSB frequency | 640320 | NOT 641280 — wrong value causes sync failure |
| Valid FR1 PRB | 11, 24, 38, 51, 65, 78, 92, 106 | Cannot use arbitrary PRB counts |

### Test Results

```
CMDLINE: ./nr-softmodem -O ~/gnb-du.sa.band78.24prb.usrpb210.conf --rfsim

[GNB_APP] F1AP: gNB idx 0 gNB_DU_id 1, gNB_DU_name gNB-Pi5-24PRB-DU
[GNB_APP] Configured DU: cell ID 12345678, PCI 0
[F1AP] Starting F1AP at DU
[F1AP] F1-C DU IPaddr 10.85.42.8, connect to F1-C CU 10.76.170.45
```

**Pi 5 DU ran stably for 15+ min without any ERROR_CODE_OVERFLOW or crash.**

---

## CU Status on serber-firecell

The serber-firecell AMF is running correctly:

| Component | IP Address | Status |
| --- | --- | --- |
| AMF (SCTP) | 10.76.170.45:38412 | Listening (host network mode) |
| MySQL | 10.76.170.45:3306 | Running |
| SMF | 10.76.170.45 | Running |
| UPF | 10.76.170.45 | Running |


---

## Key Finding: Bandwidth vs Stability

| Bandwidth | PRB | Pi 5 CPU Load | Status               |
| --------- | --- | ------------- | -------------------- |
| 40 MHz    | 106 | 100%+         | CRASH                |
| 20 MHz    | 51  | ~80%          | Unknown (not tested) |
| 10 MHz    | 24  | ~40-60%       | STABLE               |

For the Pi 5 to act as a DU, we simply reduce the bandwidth.

---

## Testing Progress

| Scenario                  | Status   | Notes                       |
| ------------------------- | -------- | --------------------------- |
| Pi 5 as DU at 106 PRB     | CRASH    | Overflow after 2-3s         |
| Pi 5 as DU at 24 PRB      | SUCCESS  | L1 stable, no crash         |
| USRP B210 hardware        | COMPLETE | 61.44 MHz validated         |
| Pi 5 as DU (rfsim)        | COMPLETE | NGAP connection works       |
| serber-minipc full stack  | COMPLETE | 3+ hours stable             |
| PWS/SIB8 code             | COMPLETE | Abdullah patch, compiles ok |
| CU/DU split (F1-C)        | PARTIAL  | DU ok, CU ok                |
| UE registration at 24 PRB | PENDING  | Not yet tested              |

---

## Machines

| Machine          | IPs                               | Role                       | Status |
| ---------------- | --------------------------------- | -------------------------- | ------ |
| serber-firecell  | 10.76.170.45                      | Core Network + CU          | AMF working, CU crashed |
| serber-minipc    | 10.85.168.144, 10.0.0.2          | Full stack capable DU     | Working |
| serber-pi        | 10.76.170.117, 10.85.42.8 (WiFi) | DU (Pi 5, 4GB)            | Working at 24 PRB |

---

## serber-minipc Benchmark

For reference — serber-minipc can run the full 5G stack on its own:

| Component | Value |
| --- | --- |
| CPU | Intel N95 (4 cores @ 3.1 GHz) |
| RAM | 15 GB DDR5 |

| Component         | CPU Usage   | Memory Usage    |
| ----------------- | ----------- | --------------- |
| DU (nr-softmodem) | 18–30%      | 850 MB          |
| CN (7 containers) | ~5–8% total | ~450 MB total   |
| TOTAL         | ~25–35% | ~1.3 GB     |
| System Idle       | ~92–97%     | 12 GB available |

**Conclusion:** serber-minipc (Intel N95) is more than capable of running the full 5G stack with significant headroom.

---

## Next Steps

1. Start CU on serber-firecell (fix SIGSEGV on SCTP bind)
2. Complete F1-C SCTP connection between Pi 5 DU and CU
3. Test actual UE registration at 24 PRB
4. Consider even lower PRB (11 PRB = 5 MHz) if further stability needed
5. Alternative: Run CU on serber-minipc instead of serber-firecell

---

## Device Comparison: Weight & Power Consumption

![Weight and Power Comparison](weight_power_comparison.png)

| Device | Weight | Power Consumption (Typical) |
| --- | --- | --- |
| Raspberry Pi 5 | 46g | ~6W |
| Jetson Orin Nano | 174g | ~10W |
| Acemagic S1 Mini PC | 391.2g | ~25W |

---

## Summary

| What Works                   | Status                      |
| ---------------------------- | --------------------------- |
| Pi 5 at 106 PRB              | CRASH (2-3s)                |
| Pi 5 at 24 PRB               | STABLE                      |
| USRP B210 hardware           | Working                     |
| Pi 5 DU initialization       | Working                     |
| CU/DU split concept          | Viable at lower bandwidth   |
| Pi 5 real-time L1 processing | Solvable with 10 MHz config |
| serber-minipc full stack     | Working                     |
| PWS/SIB8 code                | Working                     |