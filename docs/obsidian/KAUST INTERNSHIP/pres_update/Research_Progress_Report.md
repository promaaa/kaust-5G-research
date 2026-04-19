# Research Progress Report - OAI 5G Setup Update

**Date:** April 18, 2026
**Last Updated:** Session end - All attempts to fix Jetson SCTP exhausted

---

## What Works: OAI 5G Core Network

| Component                     | IP Address     | Status                   |
| ----------------------------- | -------------- | ------------------------ |
| `rfsim5g-oai-amf`             | 192.168.71.132 | ✅ Healthy                |
| `rfsim5g-oai-smf`             | 192.168.71.133 | ✅ Healthy                |
| `rfsim5g-oai-upf`             | 192.168.71.134 | ✅ Healthy                |
| `rfsim5g-mysql`               | 192.168.71.131 | ✅ Healthy                |
| `rfsim5g-oai-gnb` (on oai-pc) | 192.168.71.140 | ✅ Healthy                |
| `rfsim5g-oai-nr-ue`           | 192.168.71.150 | ✅ Connected, IP 12.1.1.2 |

**Verification:**
```bash
docker exec rfsim5g-oai-nr-ue ping -c 3 12.1.1.1
# 64 bytes from 12.1.1.1: icmp_seq=1 ttl=64 time=59.2 ms
```

**Full 5G SA network with gNB + UE is working on oai-pc.**

---

## The Problem: Jetson Orin Nano Cannot Run DU

**Jetson Orin Nano (10.85.156.17)** is meant to be the RAN/DU but is blocked from running OAI gNB/DU due to missing SCTP support in the kernel.

```
Error when trying SCTP:
socat - SCTP-LISTEN:38412
Protocol not supported

Error when trying to load SCTP module:
sudo modprobe sctp
FATAL: Module sctp not found in directory /lib/modules/5.15.148-tegra
```

| Interface | Protocol | Status |
|-----------|----------|--------|
| N2 (gNB ↔ AMF) | SCTP | ❌ BLOCKED |
| F1-C (CU ↔ DU) | SCTP | ❌ BLOCKED |

**Without SCTP, no OAI gNB/CU/DU can run on the Jetson.**

---

## Root Cause Analysis

### Kernel Information
```
Linux version 5.15.148-tegra (buildbrain@mobile-u64-6354-d6000)
(aarch64-buildroot-linux-gnu-gcc.br_real (Buildroot 2022.08) 11.3.0)
#1 SMP PREEMPT Thu Sep 18 15:08:33 PDT 2025
```

### Why SCTP Doesn't Work
```
CONFIG_IP_SCTP is not set   # SCTP disabled in kernel config
```

NVIDIA built the Jetson kernel **without SCTP support**. The kernel configuration has `CONFIG_IP_SCTP=n` - SCTP is not compiled as a module or built-in.

### What We Discovered

1. **NVIDIA Uses Custom Toolchain:** Buildroot 2022.08 with gcc 11.3.0
2. **Kernel Is Locked:** Cannot simply `modprobe sctp` - module doesn't exist
3. **Building SCTP Module Is Possible But Complex:** We downloaded NVIDIA kernel sources and built the module, but it won't load due to toolchain mismatch

---

## All Attempts to Fix Jetson SCTP (FAILED)

We attempted **12 different approaches** to enable SCTP - all failed.

### Attempt 1: modprobe sctp ❌
```
FATAL: Module sctp not found in directory /lib/modules/5.15.148-tegra
```

### Attempt 2: Build from Ubuntu Kernel Source ❌
```
Exec format error - Wrong architecture/toolchain
```

### Attempt 3: Build from NVIDIA Source (Ubuntu Toolchain) ❌
```
sctp: disagrees about version of symbol inet6_add_protocol
sctp: Unknown symbol inet6_add_protocol (err -22)
[... 297 similar symbol version errors ...]
```

### Attempt 4: Force Load with --force-vermagic ❌
```
modprobe: ERROR: could not insert 'sctp': Exec format error
```

### Attempt 5: Install Generic Ubuntu Kernel ❌
No arm64 generic kernel available for Jetson platform.

### Attempt 6: Use Existing SCTP from Other Kernel ❌
```
no symbol version for module_layout
```

### Attempt 7: Full Kernel Build (make modules) ❌
`Module.symvers` never created - build stalled after 30+ minutes.

### Attempt 8: Download NVIDIA Buildroot Toolchain ❌
```
ERROR 404: Not Found (URL requires login)
```

### Attempt 9: Userspace-Only SCTP ❌
Won't work - OAI nr-softmodem needs kernel SCTP sockets.

### Attempt 10: Pre-built SCTP Search ❌
No pre-built SCTP module exists anywhere on Jetson.

### Attempt 11: Kernel Updates ❌
Newer kernel (5.15.0-1057) available but may not have SCTP either.

### Attempt 12: Kernel Cmdline Parameters ❌
SCTP cannot be enabled at runtime - must be compiled into kernel.

---

## Why Everything Failed

### The Core Issue: Toolchain Mismatch

When we built SCTP module from NVIDIA sources:
- **Build environment:** Ubuntu gcc 11.4.0
- **Running kernel:** Built with Buildroot gcc 11.3.0

Even though the **source code was identical**, the compiled symbol versions differ. Linux kernel uses "symbol versioning" (CRC checks) to ensure modules match the exact kernel they were built against.

```
Our module vermagic:     5.15.148-tegra SMP preempt mod_unload modversions aarch64
Running kernel expects:  (different CRC values for each symbol)
```

### The Catch-22

1. To build a compatible SCTP module, we need NVIDIA's Buildroot toolchain
2. NVIDIA's toolchain download URL returns 404 (requires developer login)
3. Without the exact toolchain, the module cannot load
4. Without SCTP, we cannot run OAI DU on Jetson

---

## Current Workaround

For immediate testing, we are running the **OAI gNB on oai-pc** instead of Jetson:

```
[Jetson Orin Nano] <-- currently idle -->
                           |
                     [oai-pc gNB]
                           |
                     [Core Network]
```

The oai-pc has a standard Ubuntu kernel with SCTP support built-in, so everything works there.

---

## Solution Path for Next Session

### What We Need

To build a compatible SCTP module for Jetson, we need:

1. **NVIDIA Buildroot Toolchain:** `aarch64--glibc--stable-2022.08-1`
   - GCC 11.3.0 from Buildroot 2022.08
   - Same toolchain NVIDIA used to build the kernel

2. **Steps to Apply Fix:**
   ```bash
   # 1. Get toolchain from Bootlin (requires account):
   # https://bootlin.com/pub/releases/toolchains/aarch64--glibc--stable-2022.08-1.tar.xz

   # 2. Set CROSS_COMPILE
   export CROSS_COMPILE=$HOME/l4t-gcc/aarch64--glibc--stable-2022.08-1/bin/aarch64-buildroot-linux-gnu-

   # 3. Rebuild SCTP module
   cd ~/Downloads/Linux_for_Tegra/source/kernel/kernel-jammy-src/
   make M=net/sctp modules

   # 4. Install and load
   sudo cp net/sctp/sctp.ko /lib/modules/5.15.148-tegra/updates/
   sudo modprobe sctp
   ```

### Alternative Solutions

1. **NVIDIA SDK Manager:** Reflash with official kernel (requires full reflash)
2. **Run DU on oai-pc:** Keep Jetson for RF only (USRP B210 when it arrives)
3. **Wait for NVIDIA to enable SCTP:** File a feature request/bug report

---

## Files and Locations

### On Jetson (10.85.156.17)
| File | Description |
|------|-------------|
| `~/Downloads/public_sources.tbz2` | NVIDIA R36.4.4 sources (216MB) |
| `~/Downloads/Linux_for_Tegra/` | Extracted kernel source |
| `/lib/modules/5.15.148-tegra/updates/sctp.ko` | Our (broken) SCTP module |
| `/var/log/syslog` | System logs |

### On oai-pc (10.85.143.198)
| File | Description |
|------|-------------|
| `/home/oai/openairinterface5g/` | OAI source code |
| `/home/oai/Documents/oai_jetson_sctp_context.md` | Next session guide |
| `/home/oai/Documents/oai_jetson_sctp_failed_attempts.md` | All failed attempts |

---

## Quick Start Commands

```bash
# Start OAI 5G on oai-pc (currently working)
cd /home/oai/openairinterface5g/ci-scripts/yaml_files/5g_fdd_rfsimulator
docker compose up -d mysql oai-amf oai-smf oai-upf oai-ext-dn
docker compose up -d oai-gnb
docker compose up -d oai-nr-ue

# Verify
docker exec rfsim5g-oai-nr-ue ping -c 3 12.1.1.1
```

---

## Next Steps

| Priority | Task | Status |
|----------|------|--------|
| 1 | Get NVIDIA Buildroot toolchain (gcc 11.3.0) | PENDING |
| 2 | Rebuild SCTP module with correct toolchain | PENDING |
| 3 | Load SCTP on Jetson | PENDING |
| 4 | Test gNB/DU on Jetson | PENDING |
| 5 | Direct Ethernet connection (Phase 2) | PENDING |
| 6 | USRP B210 integration (Phase 3) | PENDING |

---

## References

- [NVIDIA Jetson Linux R36.4.4](https://developer.nvidia.com/embedded/jetson-linux-r3644)
- [NVIDIA Kernel Customization Guide](https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/Kernel/KernelCustomization.html)
- [Failed Attempts Document](/home/oai/Documents/oai_jetson_sctp_failed_attempts.md)
- [Next Session Context](/home/oai/Documents/oai_jetson_sctp_context.md)
