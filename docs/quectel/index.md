### Quectel Modem Setup

This document describes how to set up a Quectel cellular modem on Linux.

Check [this document](https://www.quectel.com/download/quectel_umts_lte_5g_linux_usb_driver_user_guide_v3-2/) from Quectel for more information.

---

## 1. Prerequisites

### Check that the modem is visible:

```bash
lsusb
```

A Quectel device should appear.

### Verify drivers are loaded:

```bash
lsmod | egrep 'cdc_wdm|cdc_mbim|qmi_wwan'
```

If `qmi_wwan` or `cdc_mbim` is active, a network interface should exist:

```bash
ip link
```

Expected interface:

```
wwan0
```

### Check serial Ports (TTY):

```bash
ls /dev/ttyUSB*
```

Quectel modems expose multiple USB serial interfaces.

Typical mapping(as Quectel states in its [document](https://www.quectel.com/download/quectel_umts_lte_5g_linux_usb_driver_user_guide_v3-2/)): 

* `ttyUSB0` – DIAG
* `ttyUSB1` – GNSS
* `ttyUSB2` – AT command
* `ttyUSB3` – Modem

---

## 2. Access AT Command Interface

Install and run `minicom`:

```bash
sudo apt install minicom
sudo minicom -D /dev/ttyUSB2 -b 115200
```

The following AT commands must be executed to register the module on the 5G Standalone (SA) network, along with the expected responses:

```
# display module’s identification information
ATI
Quectel
RM500Q-GL
Revision: RM500QGLABR11A06M4G
OK

#Set the DNN as defined in the Core Network:
AT+CGDCONT= 1,"IP","oai","",0,0,0

# display functionality level. 1 means that the module is fully functional
AT+CFUN?
+CFUN: 1
OK
# query if SIM card is operational
AT+CPIN?
+CPIN: READY
OK

# We can try to lock to 5G with following command to test.
AT+QNWPREFCFG="mode_pref" // Query the current network search mode
AT+QNWPREFCFG="mode_pref",NR5G // Lock to NR5G
# We can configure one 5G band like N78
AT+QNWPREFCFG: "nr5g_band",78

# display the available DNNs
AT+CGDCONT?
+CGDCONT: 1,"IP","oai","0.0.0.0",0,0,0,0,,,,,,,,,"",,,,0
OK

# display the network information of the serving cell. “NOCONN” means that the UE camps on that cell and has registered on the network, and it is in idle mode.
AT+QENG="servingcell"
+QENG:
"servingcell","NOCONN","NR5G-SA","TDD",999,70,E00,0,1,641280,78,6,-67,-11,31,1,-
OK

# display the current operator
AT+COPS?
+COPS: 0,0,"999 70 Magic",11
OK

# Antenna Receive power level 
AT+QRSRP
+QRSRP: -94,-88,-44,-44,NR5G
OK

# display the access technology selected, the operator and the band selected
AT+QNWINFO
+QNWINFO: "TDD NR5G","99970","NR5G BAND 78",641280
OK

# display the allocated IP address
AT+CGPADDR=1
+CGPADDR: 1,"12.1.1.2"
OK

#IMPORTANT: Configures the module to expose a QMI-based USB networking interface. You can set '2' instead for MBMI, but using MBMI we were not able to successfully start a PDU session and get an IP address, thus we used QMI.
AT+QCFG="usbnet",0
AT+CFUN=1,1 //Reboot the module
```

`Ctrl + A` then `X` to exit `minicom`.

---

## 3. Quectel QConnectManager

Quectel provides `QConnectManager` as a user-space tool for managing QMI/MBIM connections. See [documentation](https://www.quectel.com/download/quectel_qconnectmanager_linux_user_guide_v1-0/).

Clone and build:

```bash
git clone https://github.com/QuectelWB/q_drivers.git
cd q_drivers/Quectel_QConnectManager_Linux_V1.6.8
ln -s QCQMUX.c MPQMUX.c
ln -s QCQMUX.h MPQMUX.h
autoreconf -i
./configure
make -j$(nproc)
```

If compilation fails due to strict warnings, rebuild with relaxed flags:

```bash
make clean
make -j$(nproc) CFLAGS="-O1 -Wall -Wextra -Wno-error -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0"
```

Verify compilation:

```bash
ls -l quectel-CM quectel-qmi-proxy quectel-mbim-proxy
```

Install and configure `udhcpc`:

```bash
sudo apt install udhcpc

sudo install -m 755 ./default.script /etc/udhcpc/default.script
sudo install -m 755 ./default.script_ip /etc/udhcpc/default.script_ip
```

Bring the interface up:

```bash
sudo ip link set wwan0 up

#verify the interface state
ip link show wwan0
```

Start `quectel-CM`:

```bash
sudo ./quectel-CM -s oai -4 -i wwan0 -v
```

You may need to reboot the system.


> [!NOTE]
> There are two ways to power off the module:
> - **Hardware shutdown:** Switch S101 to OFF.
> - **Software shutdown:** Use `AT+QPOWD` for a proper shutdown.

