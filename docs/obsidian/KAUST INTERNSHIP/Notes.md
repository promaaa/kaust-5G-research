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
UE <--- 5G Emission ---> gNB (UAV) <---Backhaul (NGAP)---> AMF

---
**NETWORK LINKS:**
1. 5G Emission: Wireless Radio Access Network (RAN) link between the gNB/UAV and the user device (UE)
2. Backhauling: Transport link (wireless or fiber) connecting the gNB/UAV-BS to the 5G Core Network
3. NGAP: Control plane interface used for signaling between the gNB and the AMF

---
**FIAP**

### DU/CU Split Parameters
| OAI Configuration Parameter        | Function                                                              | Typical Value                                                 |
| ---------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------- |
| `tr_n_preference`                  | Defines the "Northbound" network interface type (towards the CU).     | `"f1"` (Enables 3GPP functional split)                        |
| `local_n_if_name`                  | Designates the local physical or virtual interface of the DU.         | `"eth0"`, `"eth1"`, or `"lo"` (for local deployment)          |
| `local_n_address`                  | Local IP address of the DU for binding SCTP and UDP sockets.          | `192.168.1.10` (Jetson Ethernet interface address)            |
| `local_n_address_f1u`              | (Optional) Distinct IP address for GTP-U traffic only.                | Used to physically separate C and U planes on the DU.          |
| `remote_n_address`                 | Destination IP address of the CU for F1AP communication.              | `192.168.1.20` (Remote server IP address)                     |
| `local_n_portc` / `remote_n_portc` | Local and remote binding ports for the control plane (SCTP).          | `500` (Local DU port) / `501` (Remote CU port)                |
| `local_n_portd` / `remote_n_portd` | Local and remote binding ports for the user plane (GTP-U).            | `2152` (Standard defined by 3GPP)                             |

**ABBREVIATIONS OF THE TABLE**
F1: Standardized communication interface between the CU and the DU.
F1AP (F1 Application Protocol): Signaling protocol running over the F1 interface to manage link establishment and configuration between CU and DU.
SCTP (Stream Control Transmission Protocol): Reliable transport protocol used for carrying signaling (Control Plane), ensuring message ordering and integrity.
GTP-U (GPRS Tunnelling Protocol User Plane): Encapsulation protocol used to route end-user IP data through the core network and radio access.
C-Plane (Control Plane): The set of signaling and control mechanisms (session management, mobility, security).
U-Plane (User Plane): The path taken by the actual user data (e.g., internet traffic).
Socket: Technical combination of an IP address and a port number allowing two network applications to communicate.
3GPP (3rd Generation Partnership Project): The global organization that develops technical specifications and standards for mobile networks, including 5G.

