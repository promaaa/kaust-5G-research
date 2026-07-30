---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #0b0f19
color: #f8fafc
style: |
  section {
    font-family: 'Inter', sans-serif;
    background-color: #0b0f19;
    color: #94a3b8;
    padding: 35px;
    font-size: 26px;
  }
  h1, h2, h3 {
    font-family: 'Outfit', sans-serif;
    color: #f8fafc;
    font-weight: 800;
  }
  h2 {
    color: #38bdf8;
    border-bottom: 2px solid #1e293b;
    padding-bottom: 10px;
    margin-top: 0px;
  }
  footer {
    font-size: 0.5em;
    color: #475569;
  }
  strong {
    color: #f8fafc;
  }
  ul {
    margin-left: 20px;
  }
  .grid {
    display: grid;
    grid-template-columns: 1fr 1.3fr;
    gap: 20px;
  }
  .card-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .card {
    background: #1e293b;
    border-radius: 8px;
    padding: 12px;
    border: 1px solid #334155;
    font-size: 0.8em;
  }
  .card-title {
    font-weight: bold;
    color: #fbbf24;
  }
  .badge {
    background: #10b981;
    color: #0b0f19;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.8em;
    font-weight: bold;
    float: right;
  }
  .badge.pending {
    background: #f59e0b;
  }
---

# From Ground Station to Flying 5G Relay
### Progress on a Drone-Oriented 5G Testbed

Research Progress Recap
Presenter: Research Team

---

## The idea in one picture

<div class="grid">
<div>

**Project Concept**

Instead of carrying an entire heavy 5G base station on a drone, we **separate the lightweight radio** parts from the heavy computing intelligence on the ground.

The core network brain stays safe on the ground, while the drone serves as a lightweight flying relay.

</div>
<div>

![width:600px](assets/diagrams/project-concept.svg)

</div>
</div>

---

## Why this project matters

<div class="grid">
<div>

**Disaster & Emergency Coverage**

Temporary coverage is vital after **floods, forest fires, or critical outages** where ground infrastructure is destroyed.

A drone can **restore emergency coverage within minutes**. The challenge is keeping airborne equipment light and power-efficient.

</div>
<div>

![width:600px](assets/diagrams/emergency-use-case.svg)

</div>
</div>

---

## What CU/DU split means

<div class="grid">
<div>

**Architecture Concept**

We divide a 5G base station into two parts:

* **Core Network & CU**: The ground-based "brain" managing user sessions, security, and protocols.
* **DU & Radio antenna**: The drone-carried "relay" transmitting actual high-speed radio waves.
* **Backhaul Link (F1)**: Wireless connection linking them.

</div>
<div>

![width:600px](assets/diagrams/cu-du-split.svg)

</div>
</div>

---

## The physical testbed

<div class="grid">
<div>

**Hardware Setup**

We validated a real-world benchtop setup using accessible hardware:

* **serber-firecell**: Ground Core & CU.
* **serber-minipc**: Remote DU unit.
* **Raspberry Pi 5**: Portable DU candidate.
* **USRP B210**: Software-programmable antenna.
* **Quectel Modem**: Wireless backhaul link.

</div>
<div>

![width:520px](assets/picture-of-setup.png)

</div>
</div>

---

## Progress timeline

<div class="grid">
<div>

**Milestones Timeline**

The system progressed systematically from software simulations to real-world wireless hardware loops.

Key achievements include connecting a **commercial phone**, broadcasting **emergency warnings (PWS)**, and implementing **5G WireGuard backhauling**.

</div>
<div>

![width:600px](assets/diagrams/progress-timeline.svg)

</div>
</div>

---

## The main engineering pivots

<div class="grid">
<div>

**Hurdles & Adaptations**

Faced with real-world hardware limits, the project shifted direction to find viable solutions:

We resolved **protocol blocks, hardware overloading, and signal saturation** to reach a stable prototype.

</div>
<div class="card-container">

<div class="card">
<div class="card-title">1. Jetson Kernel and I/O</div>
A custom SCTP kernel plus CPU, IRQ, and USB tuning made the embedded DU viable.
</div>

<div class="card">
<div class="card-title">2. Single-Radio Overload</div>
One radio could not serve both access and backhaul. Dedicated B210 to phone, and Quectel modem to backhaul.
</div>

<div class="card">
<div class="card-title">3. Transport and Scheduler</div>
MTU/MSS and BLER-threshold tuning removed the early 23 Mbps split ceiling.
</div>

</div>
</div>

---

## What works today

<div class="grid">
<div>

**Current Status**

Our current system has successfully validated all key features of the split 5G architecture.

The remaining work is to turn best-observed runs into a controlled, publishable
measurement campaign and complete the flight integration.

</div>
<div class="card-container" style="font-size: 0.75em;">

* **Commercial phone attached** <span class="badge">Done</span>
* **Public Warning System SIB8** <span class="badge">Done</span>
* **CU/DU split F1 separation** <span class="badge">Done</span>
* **Wireless F1 tunnel over WiFi/5G** <span class="badge">Done</span>
* **Raspberry Pi 5 DU timing fix** <span class="badge">Done</span>
* **End-to-end backhaul speed** <span class="badge">Done</span>
* **Split scheduler bottleneck fix** <span class="badge">Done</span>
* **Repeated benchmark campaign** <span class="badge pending">Pending</span>
* **Flight integration** <span class="badge pending">Pending</span>

</div>
</div>

---

## Current target architecture

<div class="grid">
<div>

**System Layout**

* **Ground**: 5G core, CU, and donor cell.
* **Payload**: Embedded DU, access SDR, and Quectel modem.
* **Transport**: WireGuard carries F1-C and F1-U over the donor 5G link.

</div>
<div>

![width:620px](assets/diagrams/target-architecture.svg)

</div>
</div>

---

## Tuning removed the early 23 Mbps ceiling

<div class="grid">
<div>

**Best-observed throughput**

Later tests overturned the early split ceiling:

* **100 Mbps** tuned Ethernet
* **52 Mbps** Wi-Fi/GRE
* **78 Mbps** Quectel/WireGuard
* **190 Mbps** monolithic peak

**Interpretation:** MTU/MSS behavior and BLER thresholds—not the split
alone—were the recoverable constraints. Values are best observations.

</div>
<div>

![width:600px](assets/performance_comparison.png)

</div>
</div>

---

## What is next

<div class="grid">
<div>

**Roadmap to a defensible flight artifact**

The separated 5G network and wireless F1 paths now work. The next phase turns
best-observed demonstrations into a repeatable, flight-safe research artifact.

</div>
<div class="card-container" style="font-size: 0.85em;">

1. **Freeze the stack**: Publish the exact OAI revision, patches, and configs.
2. **Repeat the campaign**: Run controlled trials with synchronized metrics.
3. **Publish evidence**: Release sanitized samples and packet-path proof.
4. **Validate the light radio**: Qualify B205mini-i before choosing the small-drone path.
5. **Engineer the flight**: Bench-test power, cooling, RF isolation, mounting, and failsafes.

</div>
</div>
