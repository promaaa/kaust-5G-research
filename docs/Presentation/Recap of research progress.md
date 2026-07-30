## Recap of research progress

*Current status: Week 6 (out of 16 weeks total)*

---
### Project Vision: Drone-based Aerial Networks

<div style="font-size: 0.65em; line-height: 1.5;">

* The ultimate goal of this research is to implement a 5G NR testbed with CU/DU separation specifically tailored for drone-based aerial networks. 

* The vision is to deploy an airborne drone carrying a Distributed Unit (DU) and a USRP B210 as the RF frontend, connected via a wireless 5G backhaul to a ground station hosting the Centralized Unit (CU) and the Core Network (CN). 

* This architecture would enable flexible, rapidly deployable 5G coverage using UAVs.

</div>

---

### What changed since last update

<div style="font-size: 0.65em; line-height: 1.5;">

* **Throughput performance optimized:** achieved 23 Mbps on `serber-minipc` through the CU/DU split (eth).
* **Wireless backhaul integrated:** successfully routed F1 traffic over wifi using a GRE tunnel on `serber-minipc` with 14 Mbps throughput.
* **Repository published:** uploaded all configurations and scripts to a reproducible gh repo.

</div>

---

### Network infrastructure

<div style="font-size: 0.65em; line-height: 1.5;">

To introduce the deployment, the physical testbed is composed of four primary hardware nodes configured to represent the Core Network, CU, DU, and UE.

| Host              | Role                  | IP Address         | Operating System  |
| ----------------- | --------------------- | ------------------ | ----------------- |
| `serber-firecell` | CN & CU     | `10.76.170.38`     | Ubuntu 22.04 LTS  |
| `serber-minipc`   | DU | `10.76.170.100`    | Ubuntu 22.04 LTS  |
| `serber-pi`       | Lightweight DU        | `10.76.170.94`     | Ubuntu 22.04 (pi) |
| Nothing Phone     | UE   | Dynamic (12.1.1.2) | Android 14        |

</div>

---

## Physical testbed setup

<div style="font-size: 0.65em; line-height: 1.5; text-align: center;">

The following photograph shows the physical testbed configuration:

<div style="margin-top: 20px;">
  <img src="img/picture-of-setup.png" alt="Setup" style="max-height: 400px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border: 1px solid #ddd;">
</div>

</div>

---

### Schematics of what we are trying to achieve


![Target airborne CU/DU architecture](img/diagram-of-setup.png)


---

### Phase 1: Simulation setup

<div style="font-size: 0.65em; line-height: 1.5;">

* **Containerized CN deployment:** deployed OpenAirInterface 5G core network on `serber-firecell`.
* **Validation:** verified simulated UE attachment and packet routing using OAI's built-in RF simulator.
</div>

---

### Phase 2: Hardware block and migration

<div style="font-size: 0.65em; line-height: 1.5;">

* **Jetson kernel roadblock:** Tegra Linux kernel lacked native SCTP module support.
* **Toolchain mismatch:** custom kernel recompilations failed due to proprietary Nvidia toolchain constraints.
* **Migration:** migrated to x86 `serber-minipc` to leverage native, out-of-the-box SCTP support.
* **Stable DU:** compiled `nr-softmodem` from source to successfully link DU baseband to the CN.

</div>

---

### Phase 3: minipc/Pi 5 and real UE integration

<div style="font-size: 0.65em; line-height: 1.5;">

* **Monolithic validation:** successfully ran the full monolithic 5G stack across `serber-minipc` and `serber-firecell`.
* **Raspberry Pi baseband tuning:** benchmarked Pi 5 as a lightweight DU, resolving CPU buffer overflows by tuning to a stable 24 PRB (10 MHz) profile.
* **UE connection:** Managed to receive 5G and internet with the Nothing Phone.
* **PWS integration:** applied Abdallah's patch to be able to broadcast PWS msg.

</div>

---

### Phase 4: Split architecture and optimization

<div style="font-size: 0.65em; line-height: 1.5;">

* **F1 Split deployed:** migrated monolithic setups to a split CU/DU architecture using the USRP B210.
* **OAI paging bugfixes:** resolved memory overflows, shallow-copy double frees, and forward declarations in gNB source code.
* **Downlink BLER resolution:** solved a 74% block error rate blocking user internet traffic by tuning RF gains to `att_tx=3` and `att_rx=12` to prevent baseband saturation.

</div>

---

### Phase 5: Backhauling (wifi/5G)

<div style="font-size: 0.65em; line-height: 1.5;">

* **Baseline established:** achieved **23 Mbps** throughput over a direct physical L2 Ethernet F1 link.
* **Wireless F1 tunnel:** encapsulated F1 traffic over a university WiFi network using a custom GRE tunnel.
* **Performance:** sustained stable internet data sessions with **14 Mbps** user throughput (~60% baseline).

</div>

---

### Next steps

<div style="font-size: 0.65em; line-height: 1.5;">

1. **Full internet validation:** test and verify end-to-end internet access on a client PC running OAI UE code.
2. **Backhauling expansion:** integrate further WiFi/5G multi-path backhauling and latency profiling.

</div>
