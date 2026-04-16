# OpenAirInterface 5G Setup - Phase 1 Documentation

## Current Status

**Phase 1: University Network Connectivity - COMPLETED ✅**
- Network path verified: University network allows SCTP between machines
- OAI-CN on core machine: Running with all containers healthy
- Proxies on core: Running and functional
- **Limitation**: Jetson Orin Nano kernel lacks SCTP support

## Machines

| Hostname | IP (Wireless) | Role |
|----------|---------------|------|
| oai-pc (core) | 10.85.143.198/20 | Core Network (OAI-CN) |
| uav-bs (Jetson) | 10.85.156.17/20 | RAN (blocked - no SCTP) |

## Architecture

```
[Jetson Orin Nano] <-- University Network (N2/SCTP) --> [Core: 10.85.143.198]
                                                                        |
                                                              [Python Proxies]
                                                              - SCTP 38412 -> AMF:38412
                                                              - HTTP 8080 -> AMF:80
                                                                        |
                                                              [OAI-CN Containers]
                                                              - AMF: 192.168.71.132
                                                              - SMF, UPF, NRF, etc.
```

## What Works

| Component | Status |
|-----------|--------|
| Core machine OAI-CN | ✅ Running, all containers healthy |
| SCTP proxy (0.0.0.0:38412) | ✅ Listening, forwarding to AMF |
| HTTP proxy (0.0.0.0:8080) | ✅ Listening, forwarding to AMF |
| AMF receiving connections | ✅ Verified in AMF logs |
| University network path | ✅ Verified |
| Jetson gNB (any mode) | ❌ Fails - "Protocol not supported" |

## Root Cause: Jetson SCTP Limitation

**Jetson Orin Nano kernel `5.15.148-tegra` lacks SCTP support**

```
$ cat /proc/net/sctp/eps
ENDPT     SOCK   STY SST HBKT LPORT   UID INODE LADDRS
       0        0 2  10  26   38412  1000 3773632 0.0.0.0   <- Core machine has SCTP

$ ssh jetson cat /proc/net/sctp/eps
cat: /proc/net/sctp/eps: No such file or directory    <- Jetson has no SCTP

$ ssh jetson modprobe sctp
FATAL: Module sctp not found in directory /lib/modules/5.15.148-tegra
```

**OAI 5G requires SCTP for:**
- N2 interface (gNB ↔ AMF)
- F1-C interface (CU ↔ DU)

**Without SCTP in kernel, no gNB/CU/DU can run on Jetson.**

## Options for Phase 2+

### Option A: Use Standard Ubuntu Machine for RAN (Recommended)
- Any x86_64 or ARM64 machine with Ubuntu 22.04+
- Standard kernel has SCTP support
- Can run OAI gNB/DU in Docker
- Connect via university network or direct Ethernet

### Option B: Custom Jetson Kernel (Complex)
- Requires NVIDIA Jetson kernel sources
- Build environment with cross-compiler
- Risk: May break GPU drivers, JetPack updates
- Not recommended unless necessary

### Option C: Accept gNB Runs on Core
- Existing `rfsim5g-oai-gnb` on core already works with UE
- Use Jetson only for:
  - USRP B210 when it arrives (via USB)
  - Future Phase 2/3 with direct Ethernet

## Running Services (on oai-pc)

**Python Proxies:**
```
/tmp/sctp_proxy.py  - SCTP relay 0.0.0.0:38412 -> 192.168.71.132:38412
/tmp/http_proxy.py  - HTTP relay 0.0.0.0:8080 -> 192.168.71.132:80
```

**Docker Containers (rfsim5g-* prefix):**
```
rfsim5g-oai-amf    - 192.168.71.132:80, :38412/sctp
rfsim5g-oai-smf    - 192.168.71.133
rfsim5g-oai-upf    - 192.168.71.134, 192.168.72.134
rfsim5g-oai-gnb    - 192.168.71.140 (simulated UE connected)
rfsim5g-oai-nr-ue  - 192.168.71.181 (simulated UE)
rfsim5g-mysql      - 192.168.71.131
```

## Verified Connectivity

From AMF logs:
```
[2026-04-16 12:11:26.159] [sctp] [info]     - IPv4 Addr: 10.85.143.198
[2026-04-16 12:11:26.159] [ngap] [debug] Ready to handle new NGAP SCTP association request
```

AMF is successfully receiving SCTP connections from `10.85.143.198` (core's wireless IP).

## Next Steps

1. **Immediate**: Proceed with Phase 2 (direct Ethernet) using core machine for gNB
2. **USRP B210**: Connect to core machine directly when it arrives
3. **Alternative RAN**: Use a standard Ubuntu laptop/PC if Jetson is required for RAN
4. **Future**: Consider Option B (custom Jetson kernel) if absolutely needed

## Configuration Files

**Core (oai-pc):**
- `/tmp/gnb_config/gnb_cu.conf` - CU config for CU/DU separation
- `/tmp/gnb_config/gnb_du.conf` - DU config for CU/DU separation

**Jetson:**
- `/tmp/gnb_config/gnb_sa.yaml` - Monolithic SA config (requires SCTP - won't work)

## PLMN Configuration

- MCC: 208
- MNC: 99
- TAC: 1
- SNSSAI: SST=1, SD=0xffffff
- Band: n78 (3.5 GHz, 30 kHz SCS)