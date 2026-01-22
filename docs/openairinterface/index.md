# [OpenAirInterface](https://gitlab.eurecom.fr/oai/openairinterface5g) 
OAI is an open-source software platform that provides a full implementation of 3GPP cellular standards for both 4G LTE and 5G NR networks.
It can run in two ways:
- **Emulated mode:** The UE and gNB run as software on the same machine and
communicate through virtual interfaces
- **Over-the-air mode:** real radio signals are transmitted using SDR (Software Defined Radio). The gNB and UE can run on different machines, each connected to its own SDR, or we can use a real smartphone.
In both cases, the core network functions are deployed as containers.

## OAI Code
OAI runs different processes, each with different tasks that communicate with each other through ITTI messages.

![OAI Code Architecture](../assets/oai-code.png)

---

`nr-softmodem.c`

**main():**

* Start point.
* Create tasks and read configuration and setup different general instances (e.g. RC.nrrrc as we'll see).
* Of course it does so by calling different functions in the same file or in other files.

**create_gNB_tasks():**

1. fill general instances:
   1. RCconfig_nr_macrlc(cfg): fill RC.nrmac
   2. RCconfig_NRRRC(): fill RC.nrrrc (see 1st:call flow)
2. in addition to other tasks, it creates rrc_gnb_task which is implemented in rrc_gNB.c (see 2nd: itti_create_task flow)

---

`gnb_config.c:`

**RCconfig_NRRRC():**

* returns gNB_RRC_INST_s instance that stores some gNB RRC configuration parameters.
* create_gNB_tasks puts them in RC.nrrrc[0]
* NOTE: RC stores an RRC instance as well as Mac instance. And i believe there are others, all to be used across the program since it seems that RC is accessible from anywhere.
* Note: gNB_RRC_INST_s is same as gNB_RRC_INST, similar to gNB_MAC_INST_s and gNB_MAC_INST
* calls fill_cu_sibs

**fill_cu_sibs():**

* put in the rrc instance list of SIBs, just their types, got from config file. (in our case just sib8 as in our gNB config file we've added cu_sibs=[8]).
* it'll be used later in rrc_gNB_process_f1_setup_req

---

`rrc_gNB.c`

**openair_rrc_gNB_configuration():**

* gets the same gNB_RRC_INST_s.
* calls rrc_gNB_CU_DU_init.

**rrc_gNB_CU_DU_init():** 

* gets the same gNB_RRC_INST_s
* gets node type from the rrc struct
* switches case between monolithic, cucp, cu, du.
* prior to this point there was no difference between the cu/du split mode and the monolithic mode (or maybe there was, i didn't dive into details of all methods, but i'm talking about the f1 setup flow now).
* At this point, based on the node type mac_rrc_dl_XX_init() is called.

  * XX can be either direct or f1ap, which are written inside mac_rrc_dl_direct.c or mac_rrc_dl_f1ap.c respectively.
* In our case we're using monolithic, so we will continue through this case.

---

`mac_rrc_dl_direct.c`

**mac_rrc_dl_direct_init():**

* gets nr_mac_rrc_dl_if_t instance, which is the rrc->mac_rrc struct.

* rrc->mac_rrc basically has multiple functions that will be filled differently based on the node type.

* e.g.:

  * mac_rrc->f1_setup_response = f1_setup_response_direct;

    * This method (mac_rrc->f1_setup_response) will be called inside rrc_gNB_process_f1_setup_req later.
  * my implementation: mac_rrc->write_replace_warning_req = write_replace_warning_req_direct;

* Note that f1_setup_response_direct and write_replace_warning_req_direct are written inside the same file mac_rrc_dl_direct.c, in case of cu/du split they are inside mac_rrc_dl_f1ap.c

**f1_setup_response_direct():**

* calls directly f1_setup_response method at the mac layer, because we are in the monolithic mode and there is no intermediate tasks.
* Note that in the split case, gNB CU and DU run as different processes (different whole process not just tasks) and they may run on different physical machines, and thus 3GPP standardizes the communication and mandate SCTP as the protocol to be used. Therefore, OAI added two additional intermediate tasks to implement this protocol, but they obviously run only in the split mode.
* Just to give an example of flow differences, in case of split mode, f1_setup_response_f1ap will be called. This method won't call f1_setup_response directly because as we said this is at the mac layer which is running in a different process. Instead, it will send an itti message (itti are used between tasks of the same process, even in monolithic) to the CU_F1 task which will encode an F1AP message and transmit it to the DU_F1 task by SCTP. DU_F1 will eventually calls directly f1_setup_response (see this page for more info).
* That's why i only implemented write_replace_warning_req_direct, my main focus is on monolithic mode, but i respected oai's choice at some extent. So for future expanding, a developer has only to add the code at CU_F1 and DU_F1.

---

`rrc_gNB.c:`

**rrc_gnb_task():**

* `while (1) { // Wait for a message itti_receive_msg}`
* when a message is received, switch case to its id
* case F1AP_SETUP_REQ: call rrc_gNB_process_f1_setup_req

---

`rrc_gNB_du.c:`

**rrc_gNB_process_f1_setup_req():**

* generates mib, sib1, sibs, with addition to other things obviously.
* It uses RC.nrrrc[0]->SIBs which was generated from fill_cu_sibs
* calls build_sib8_segments
* calls rrc->mac_rrc.f1_setup_response which is in our case f1_setup_response_direct
* f1_setup_response_direct just calls f1_setup_response (See note in mac_rrc_dl_direct.c card)

---

`mac_rrc_dl_handler.c`

**f1_setup_response():**

* We're now at the MAC layer.

---

`config.c`

**nr_mac_configure_other_sib():**

* decode all other sib messages then put them inside SI messages.
* encode each SI message and put it in cc->other_sib_bcch_pdu[i] which will be used inside gNB_scheduler_bch.c later when scheduling and transmitting.
* Note: cc is nrmac->common_channels[0].

---

`nr_radio_config.c`
update_SIB1_NR_SI():

* update scheduling info in SIB1 to indicate multiple SI message each contains one SIB8
