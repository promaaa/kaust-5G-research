### Abbreviations
(get_softmodem_params()->nsa 
(get_softmodem_params()->sa
SA : Standalone - 5G gNB is connected directly to the 5G core (AMF)
NSA: Non-Standalone - 5G gNB relies on an existing 4G network (eNB) 

---

CU: Central Unit: "Intelligent" processing: RRC, PDCP protocols
DU: Distributed Unit: "Real-time" processing: RLC, MAC, PHY

The CU is itself divided into 2 parts: 
1. CU-CP : signaling (RRC, PDCP control plane)
2. CU-UP : user data (PDCP user plane, SDAP)

Monolithic 5G-RAN: CU and DU are communicating in the gNB
Disaggregated 5G-RAN: CU/DU separated communicating through F1 interface

--- 
**LAYERS:**
1. PHY: Physical Layer - lowest layer : responsible for converting data into radio signals and vice versa
2. MAC: Medium Access Control - manages access to the shared radio resources and schedules data transmission between multiple users (resource allocation, prioritization of traffic, control signaling)
3. RLC : Radio Link Control - supports reliable and error-free transmission of data over the radio link (segmentation, reassembly, error detection, correction and flow control (rate of data transmission))
4. PDCP: Packer Data Convergence Protocol - supports compression/decompression of : IP packets & user data. Header compression 

**ADDITIONAL CONTROL PLANE LAYERS**
5. RRC: Radio Resource Control: manages the establishment, maintenance, and release of the radio connection between the UE and the gNB (connection setup, mobility, managaement, control signaling for handovers) 

---
### Architecture
UE *-------5G Emission------* gNB (UAV) *-------Backhaul (NGAP)------* AMF

---
**NETWORK LINKS:**
1. 5G Emission: Wireless Radio Access Network (RAN) link between the gNB/UAV and the user device (UE) 
2. Backhauling: Transport link (wireless or fiber) connecting the gNB/UAV-BS to the 5G Core Network 
3. NGAP: Control plane interface used for signaling between the gNB and the AMF

---
**FIAP**
