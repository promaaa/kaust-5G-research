# Raspberry Pi 5 DU Setup - Status Report

## Overview
Setup of a Distributed Unit (DU) for OAI 5G on a Raspberry Pi 5 (serber-pi at 10.76.170.117)

## Completed Steps

### 1. OS & Basic Setup
- [x] Installed Debian 13 (Trixie) on Raspberry Pi 5 (4GB)
- [x] Hostname configured: `serber-pi`
- [x] SSH access configured: `serber@10.76.170.117`
- [x] Basic packages installed (git, vim, net-tools, sudo)

### 2. Network Stack
- [x] SCTP kernel module loaded and working
- [x] SCTP configured to load on boot

### 3. UHD (USRP Hardware Driver)
- [x] UHD v4.8.0.0 installed from source
- [x] UHD images downloaded (including B210 FPGA)
- [x] UHD Python bindings installed
- [ ] USRP B210 detection (hardware not yet connected)

### 4. OAI Source Code
- [x] OAI repository cloned to `~/openairinterface5g`
- [x] Develop branch checked out

### 5. asn1c Installation
- [x] Installed correct version of asn1c with APER support
- [x] Commit: 940dd5fa9f3917913fd487b13dfddfacd0ded06e (OAI-recommended)
- [x] Installed to: `/opt/asn1c/bin/asn1c`
- [x] Skeleton files copied to `/usr/local/share/asn1c/` for proper code generation

### 6. OAI gNB Build
- [x] nr-softmodem built successfully
- [x] Binary location: `~/oai-du/nr-softmodem` (136MB)
- [x] Binary type: ELF 64-bit ARM aarch64

### 7. Configuration Files
- [x] Configuration file created: `~/oai-du/gnb-sa.band78.rfsim.conf`
- [x] Build script created: `~/oai-du/build_oai_pi.sh`

## Configuration Details

### Network Configuration
- **Pi IP**: 10.76.170.117
- **Core Network (AMF)**: 10.76.170.110
- **PLMN**: MCC=208, MNC=95
- **TAC**: 0xa000 (40960)
- **gNB ID**: 0xe00 (3584)
- **Cell ID**: 12345678

### Configuration File Location
```
/home/serber/oai-du/gnb-sa.band78.rfsim.conf
```

### asn1c Version
- **Version**: v0.9.29 (from commit 940dd5fa)
- **Location**: /opt/asn1c/bin/asn1c
- **Skeletons**: /usr/local/share/asn1c/

## To Run

### RFsim Mode (no USRP needed)
```bash
cd ~/openairinterface5g/cmake_targets/ran_build/build
sudo ./nr-softmodem -O ~/oai-du/gnb-sa.band78.rfsim.conf --rfsim
```

### With USRP B210
```bash
cd ~/openairinterface5g/cmake_targets/ran_build/build
sudo ./nr-softmodem -O ~/oai-du/gnb-sa.band78.rfsim.conf
```

## Files Created

| File | Description |
|------|-------------|
| `~/oai-du/gnb-sa.band78.rfsim.conf` | DU configuration file |
| `~/oai-du/build_oai_pi.sh` | Build script for OAI |
| `~/oai-du/nr-softmodem` | Built nr-softmodem binary (136MB) |
| `~/openairinterface5g/` | OAI source code |
| `/opt/asn1c/` | asn1c compiler with APER support |
| `~/uhd/` | UHD source (for reference) |

## Next Steps

1. **Connect USRP B210** - Plug in hardware and verify detection
2. **Test RFsim mode** - Verify DU connects to core network
3. **Test with USRP** - Run full DU with radio hardware

## SSH Access

```bash
ssh serber@10.76.170.117
# Password: root4SERBER
```

## Quick Status Check

```bash
# Check hostname
hostname

# Check SCTP
cat /proc/net/sctp/assocs

# Check UHD
uhd_find_devices

# Check OAI binary
ls -lh ~/oai-du/nr-softmodem

# Check config
ls ~/oai-du/

# Test nr-softmodem help
~/oai-du/nr-softmodem --help
```