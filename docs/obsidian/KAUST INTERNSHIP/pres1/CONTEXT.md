# Research Context: Security for UAV-Based 5G-Advanced and 6G Networks

## 1. Project Meta-Information
* **Host Institutions:** King Abdullah University of Science and Technology (KAUST) & IMT Atlantique.
* **Supervisors:** Prof. Marc Dacier (KAUST), Dr. Ammar El Falou (KAUST), Prof. Charlotte Langlais (IMT Atlantique).
* **Domain:** Cybersecurity, Non-Terrestrial Networks (NTNs), 5G-Advanced / 6G Radio Access Networks (RAN).
* **Core Software:** OpenAirInterface (OAI).

## 2. High-Level Motivation & Objectives
The integration of Non-Terrestrial Networks (NTNs), specifically Unmanned Aerial Vehicles (UAVs), is a critical component of 5G-Advanced and 6G architectures. UAV-mounted Base Stations (UAV-BSs) provide rapid, deployable connectivity for disaster-prone or underserved regions. 

However, their critical role in emergency scenarios makes them prime targets for cyberattacks. The primary objective of this research is to investigate **Emergency Alert Spoofing**. 
* **The Threat:** Emergency alerts are broadcast unauthenticated. An attacker operating a rogue, lightweight UAV-BS can broadcast spoofed emergency alerts containing malicious phishing links to all user equipment (UE) in the coverage area.
* **The Goal:** Successfully replicate this attack in a controlled private 5G network, demonstrate that the phishing links are clickable on commercial UEs (Android/iOS), and subsequently propose robust mitigation techniques, culminating in a conference paper.

## 3. The Architecture Transition & The Current Roadblock
**The Initial Deployment Strategy:**
The team previously deployed a private 5G system utilizing a standard server machine and a Software Defined Radio (USRP B210) for both the core and access networks. 

To simulate the rogue UAV-BS, the project required transitioning the gNodeB (gNB) to a "lightweight" computing platform capable of being mounted on a drone. The selected hardware was the **NVIDIA Jetson Orin Nano**. 

**The Technical Collision (Why the project must pivot):**
While the Jetson Orin Nano fits the Size, Weight, and Power (SWaP) requirements for a UAV, it fundamentally fails at the rigorous, deterministic, real-time processing required by the OpenAirInterface 5G PHY layer. The attempt to run the disaggregated OAI CU/DU split on this ARM64 architecture has exposed three critical hardware flaws:

1.  **USB 3.0 Power Management Aggression:** The Jetson's power states (SC7 deep sleep / `tegra-xusb` autosuspend) constantly interrupt the USRP B210, leading to fatal UHD driver crashes.
2.  **DMA Bandwidth Saturation:** The Jetson's memory controllers cap concurrent USB 3.0 throughput at ~3 Gbps, far below the required bandwidth for stable, wide-band continuous TX/RX operations.
3.  **Instruction Set Incompatibility:** OAI relies heavily on x86 AVX-512 instructions for LDPC/Polar decoding. Emulating these via SIMDE on ARM NEON/SVE2 introduces fatal processing latency.

## 4. Directive for the Coding Agent
When drafting the presentation and speaker notes for the research supervisors, you must frame the pivot away from the NVIDIA Jetson Orin Nano not as a failure, but as an **evidence-based architectural correction**. 

The research goal remains the same: demonstrating Emergency Alert Spoofing via a portable gNB. However, to achieve a stable Radio Access Network capable of sustaining the SCTP/GTP-U links and broadcasting the spoofed System Information Blocks (SIBs), the project must temporarily abandon the ARM64 Jetson in favor of an **x86/x64 Mini-PC** (e.g., an Intel NUC or Minisforum equivalent). This maintains the "lightweight/portable" requirement for a theoretical UAV deployment while providing the native AVX instructions and stable USB power delivery required by the USRP B210 and the OAI software stack.