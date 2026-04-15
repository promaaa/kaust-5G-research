The implementation of F1AP messages is seamlessly integrated into OAI, supporting both Monolithic SA and CU/DU functional split modes. The F1 code is therefore always compiled with nr-softmodem.
This architecture ensures that even *when operating a monolithic gNB, internal information exchange always utilizes F1AP messages*.
The major difference lies in the CU/DU split scenario, where ASN.1-encoded F1AP messages (F1-C) are exchanges over SCTP, via a socket interface.

#### High-level F1-C code structure

The F1 interface is used internally between CU (mostly RRC) and DU (mostly MAC)
to exchange information. In DL, the CU sends messages as defined in files
`mac_rrc_dl_direct.c` (monolithic) and `mac_rrc_dl_f1ap.c` (for F1AP). In the
monolithic case, the RRC calls directly into the message handler on the DU side
(`mac_rrc_dl_handler.c`). In the F1 case, an ITTI message is sent to the CU
task, sending an ASN.1-encoded F1AP message. The DU side's DU task decodes the
message, and then calls the corresponding handler in `mac_rrc_dl_handler.c`.
Thus, the message flow is the same in both F1 and monolithic cases, with the
difference that F1AP encodes the messages using ASN.1 and sends over a socket.


A sequence diagram for downlink F1AP messages over the OAI CU/DU functional split:

```mermaid
sequenceDiagram
    box rgba(17,158,189,255) CU/RRC
    participant TASK_RRC_GNB
    participant TASK_CU_F1
    end
    Note over TASK_RRC_GNB: MAC/RRC callback
    TASK_RRC_GNB->>+TASK_CU_F1: F1AP message (ITTI)
    Note over TASK_CU_F1: F1 message encoding
    Note over TASK_CU_F1: ASN.1 encoding
    box Grey DU/MAC
    participant TASK_DU_F1
    participant MAC
    end
    Note over TASK_DU_F1: F1AP DL message handler
    TASK_CU_F1->>+TASK_DU_F1: SCTP (ITTI)
    Note over TASK_DU_F1: F1 message decoding
    Note over TASK_DU_F1: ASN.1 decoding
    TASK_DU_F1->>+MAC: F1AP message (function call)
    Note over MAC: MAC DL message handler
```

Alternative sequence handling (e.g. Monolithic), for downlink:

```mermaid
sequenceDiagram
    box rgba(17,158,189,255) RRC
    participant TASK_RRC_GNB
    end
    Note over TASK_RRC_GNB: mac_rrc_dl_direct.c callback
    box Grey MAC
    participant TASK_MAC_GNB
    end
    TASK_RRC_GNB->>+TASK_MAC_GNB: raw F1AP message
    Note over TASK_MAC_GNB: mac_rrc_dl_handler.c
```
