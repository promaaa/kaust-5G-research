# Nvidia Forums Post: SCTP Module Support on Jetson/Tegra Linux Kernel

---

**Title:** SCTP (Stream Control Transmission Protocol) module missing on Jetson - any solutions?

**Category:** Jetson & Embedded Systems / Jetson Nano / Jetson AGX Xavier / Jetson Orin

---

Hey everyone,

I'm working on a 5G NR research project requiring SCTP support for the F1 interface in OpenAirInterface (OAI), and I've run into a blocker with Jetson/Tegra Linux.

## The Problem

The Tegra Linux kernel (used on Jetson boards) **lacks native SCTP module support**. The SCTP kernel module (`sctp.ko`) is either:

- Not compiled into the kernel
- Not available as a loadable module
- Not included in the standard Jetson kernel builds

This is a hard blocker for OAI's F1 interface, which uses F1AP over SCTP/IP for CU/DU communication.

## What I've Tried

1. **Check kernel config** — SCTP wasn't enabled in the default kernel config
2. **Build from source** — Attempted to recompile the kernel with SCTP enabled, but hit toolchain issues (see below)
3. **Module not available** — `modprobe sctp` returns "Module not found"

## Why Kernel Recompilation Failed

I tried building a custom kernel with SCTP enabled, but ran into:

- **Proprietary Nvidia toolchain constraints** — The Jetson uses a custom/toolchain that's difficult to replicate
- **Build environment issues** — Even with L4T sources, the kernel build process is non-trivial
- **No out-of-the-box SCTP** — Unlike desktop/server Linux distros, Jetson doesn't ship with SCTP support

## The Workaround (For Now)

I ended up migrating to an **x86 mini PC** (Intel-based) which has native, out-of-the-box SCTP support and works perfectly.

## Questions

1. Is there an **official or community kernel module** for SCTP on Jetson?
2. Has anyone successfully **built SCTP into the Tegra kernel**? Any guides?
3. Are there **pre-built kernel images** with SCTP enabled for Jetson?
4. Is there a **userspace SCTP library** (like usrsctp) that could work as a permanent alternative?
5. Is this on Nvidia's **roadmap** to include in future L4T releases?

## System Info

- **Board:** Jetson (testing on Nano/AGX Xavier/Orin)
- **JetPack/L4T Version:** Latest (5.x/6.x)
- **Kernel:** Tegra Linux (custom)
- **Use case:** 5G NR CU/DU split with OpenAirInterface

Any insights, workarounds, or existing solutions would be greatly appreciated!

---

**Tags:** jetson, sctp, kernel, linux, openairinterface, 5g, tegra
