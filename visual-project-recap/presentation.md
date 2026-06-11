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

## Slide 1 — The idea in one picture

<div class="grid">
<div>

**Project Concept**

Instead of carrying an entire heavy 5G base station on a drone, we **separate the lightweight radio** parts from the heavy computing intelligence on the ground.

The core network brain stays safe on the ground, while the drone serves as a lightweight flying relay.

</div>
<div>

```mermaid
graph TD
    subgraph Ground["Ground Station"]
        A["Core Network + CU<br>(Heavy Computing)"]
    end
    subgraph Air["Drone Relay"]
        B["DU + USRP B210 Radio<br>(Lightweight RF Payload)"]
    end
    subgraph User["Emergency Area"]
        C["Nothing Phone User<br>(PWS Warning Alert)"]
    end
    A -->|"WireGuard (F1-C/U)"| B
    B -.->|"5G n78 Access Link"| C
    style Ground fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc
    style Air fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc
    style User fill:#1e293b,stroke:#f43f5e,stroke-width:2px,color:#f8fafc
```

</div>
</div>

---

## Slide 2 — Why this project matters

<div class="grid">
<div>

**Disaster & Emergency Coverage**

Temporary coverage is vital after **floods, forest fires, or critical outages** where ground infrastructure is destroyed.

A drone can **restore emergency coverage within minutes**. The challenge is keeping airborne equipment light and power-efficient.

</div>
<div>

```mermaid
flowchart TD
    Disaster["Disaster Event<br>(Floods, Fires, Outages)"] --> Outage["Ground Towers Broken<br>(No Cellular Signal)"]
    Outage --> Rescue["Drone 5G Relay<br>(Deploys in Minutes)"]
    Rescue --> Recovery["Emergency Coverage Restored<br>(PWS Warning Sent)"]
    style Disaster fill:#1e293b,stroke:#ef4444,stroke-width:2px,color:#f8fafc
    style Outage fill:#1e293b,stroke:#ef4444,stroke-width:2px,color:#f8fafc
    style Rescue fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc
    style Recovery fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc
```

</div>
</div>

---

## Slide 3 — What CU/DU split means

<div class="grid">
<div>

**Architecture Concept**

We divide a 5G base station into two parts:

* **Core Network & CU**: The ground-based "brain" managing user sessions, security, and protocols.
* **DU & Radio antenna**: The drone-carried "relay" transmitting actual high-speed radio waves.
* **Backhaul Link (F1)**: Wireless connection linking them.

</div>
<div>

![width:440px](assets/diagram-of-setup.png)

</div>
</div>

---

## Slide 4 — The physical testbed

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

![width:440px](assets/picture-of-setup.png)

</div>
</div>

---

## Slide 5 — Progress timeline

<div class="grid">
<div>

**Milestones Timeline**

The system progressed systematically from software simulations to real-world wireless hardware loops.

Key achievements include connecting a **commercial phone**, broadcasting **emergency warnings (PWS)**, and implementing **5G WireGuard backhauling**.

</div>
<div>

```mermaid
flowchart LR
    A["Simulation"] --> B["Real Radio"] --> C["Nothing Phone"] --> D["Emergency PWS"] --> E["Ethernet Split"] --> F["Pi 5 DU"] --> G["WiFi GRE"] --> H["Quectel 5G"] --> I["Target Setup"]
    style A fill:#1e293b,stroke:#3b82f6,color:#f8fafc
    style B fill:#1e293b,stroke:#3b82f6,color:#f8fafc
    style C fill:#1e293b,stroke:#10b981,color:#f8fafc
    style D fill:#1e293b,stroke:#10b981,color:#f8fafc
    style E fill:#1e293b,stroke:#10b981,color:#f8fafc
    style F fill:#1e293b,stroke:#10b981,color:#f8fafc
    style G fill:#1e293b,stroke:#f59e0b,color:#f8fafc
    style H fill:#1e293b,stroke:#f59e0b,color:#f8fafc
    style I fill:#1e293b,stroke:#f59e0b,color:#f8fafc
```

</div>
</div>

---

## Slide 6 — The main engineering pivots

<div class="grid">
<div>

**Hurdles & Adaptations**

Faced with real-world hardware limits, the project shifted direction to find viable solutions:

We resolved **protocol blocks, hardware overloading, and signal saturation** to reach a stable prototype.

</div>
<div class="card-container">

<div class="card">
<div class="card-title">1. Tegra Kernel Roadblock</div>
Jetson Orin Nano lacked SCTP protocol support. Pivoted to x86 and Pi 5 for native kernel support.
</div>

<div class="card">
<div class="card-title">2. Single-Radio Overload</div>
One radio could not serve both access and backhaul. Dedicated B210 to phone, and Quectel modem to backhaul.
</div>

<div class="card">
<div class="card-title">3. Throughput Bottleneck</div>
Upgrading DU strength did not remove split-mode speed limits. Shifted focus to OAI scheduler tuning.
</div>

</div>
</div>

---

## Slide 7 — What works today

<div class="grid">
<div>

**Current Status**

Our current system has successfully validated all key features of the split 5G architecture.

Performance optimization and final user-traffic validation over the wireless backhaul link are currently under active testing.

</div>
<div class="card-container" style="font-size: 0.75em;">

* **Commercial phone attached** <span class="badge">Done</span>
* **Public Warning System SIB8** <span class="badge">Done</span>
* **CU/DU split F1 separation** <span class="badge">Done</span>
* **Wireless F1 tunnel over WiFi/5G** <span class="badge">Done</span>
* **Raspberry Pi 5 DU timing fix** <span class="badge">Done</span>
* **End-to-end backhaul speed** <span class="badge pending">Testing</span>
* **Split scheduler bottleneck fix** <span class="badge pending">Testing</span>

</div>
</div>

---

## Slide 8 — Current target architecture

<div class="grid">
<div>

**System Layout**

Our unified architecture runs on a single central server:

* **serber-firecell (Ground)**: Runs 5G Core, CU, and donor base station.
* **serber-minipc (Remote)**: Runs DU, access B210, and Quectel modem.
* **WireGuard Tunnel**: Over the Quectel 5G link, carrying F1-C &amp; F1-U.

</div>
<div>

```mermaid
graph TD
    subgraph Ground["Ground Station (serber-firecell)"]
        Core["OAI 5G Core"]
        CU["OAI Central Unit (CU)"]
        Donor["OAI Donor Cell (gNB)<br>(PCI 1, TAC 2)"]
        Core --- CU
        Core --- Donor
    end
    subgraph Remote["Remote Unit (serber-minipc)"]
        Quectel["Quectel 5G Modem<br>(IP 10.0.0.6)"]
        DU["OAI Distributed Unit (DU)<br>(PCI 0, TAC 1)"]
        B210["USRP B210 Access Radio"]
        DU --- B210
    end
    subgraph UE["User Device"]
        Phone["Nothing Phone"]
    end
    
    Donor -.->|"5G RF Link"| Quectel
    Quectel == "WireGuard F1 Link" ==> CU
    B210 -.->|"5G RF Access"| Phone
    
    style Ground fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc
    style Remote fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc
    style UE fill:#1e293b,stroke:#f43f5e,stroke-width:2px,color:#f8fafc
```

</div>
</div>

---

## Slide 9 — Results and remaining bottleneck

<div class="grid">
<div>

**Throughput Benchmarks**

While monolithic 5G achieves 150 Mbps, split mode drops to **23 Mbps**. Moving the DU to stronger hardware did not increase speed.

The scheduler pins transmission rates to the lowest setting (**MCS 0**) due to delayed channel reports.

</div>
<div>

![width:440px](assets/performance_comparison.png)

</div>
</div>

---

## Slide 10 — What is next

<div class="grid">
<div>

**Roadmap to Flight**

We have moved from simulation to a real, separated 5G network with wireless backhaul.

**Our next challenge is making this setup fast, reproducible, and ready for drone flights.**

</div>
<div class="card-container" style="font-size: 0.85em;">

1. **Prove Backhaul Path**: Confirm phone traffic runs strictly over Quectel counters.
2. **Tune Scheduler**: Break the 23 Mbps limit.
3. **Package Code**: Secure configurations.
4. **Validate Pi 5 DU**: Re-test Pi DU on backhaul.
5. **Airborne Flight**: Transition to flight.

</div>
</div>
