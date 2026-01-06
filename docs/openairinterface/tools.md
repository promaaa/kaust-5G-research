## Tools

### Wireshark - Capture NR packets
Wireshark captures packets between the gNB and the core network, and RRC/MAC PDUs sent from the gNB to users.

In order to monitor core network packets you can simply open oai-cn5g interface in wireshark and filter on `ngap or gtp`.

However, with regard to PDUs from the gNB you have to do the following steps:
1. Compile tracer executable:
```
cd openairinterface5g/common/utils/T/tracer/
sudo apt-get install libxft-dev
make
```
 2. Configure wireshark:
- Use a recent version of wireshark.
- Listen on the local interface (lo) and set the filter to `udp.port==9999`.
- In the menu, choose `Edit->Preferences`.
- In the preference window, unroll `Protocols`.
- Go to `UDP` and activate `Try heuristic sub-dissectors first`.
- Go to `MAC-NR`. Select:
	- `Attempt to decode BCCH, PCCH and CCCH data using NR RRC dissector`
	- `Attempt to dissect LCID 1-3 as srb1-3`
	- For `Source of LCID -> drb channel settings`:
		- choose option `From static table`.
		- click the `Edit...` button of `LCID -> DRB Mappings Table`.
		- In the new window, click on `+`. Choose LCID `4`, DRBID `1`, UL RLC Bearer Type `AM, SN Len=18`, same thing for DL RLC Bearer Type.
- Go to `NAS-5GS`, select:
	- `Try to detect and decode 5G-EA0 ciphered messages`
- Click **OK**.

- In the menu, choose `Analyze`. In the `enabled protocols` window, search for `nr` and select `mac_nr_udp` to have `MAC-NR over UDP`.

- Run gNB by adding `--T_stdout 2` to the command. The new command becomes:
```
sudo ./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf -E --continuous-tx --T_stdout 2
```

- In another terminal run:
```
cd openairinterface5g/common/utils/T/tracer
./macpdu2wireshark -d ../T_messages.txt -live
```

### [Scat](https://github.com/fgsect/scat/tree/master?tab=readme-ov-file)
This application shows logs messages from Qualcomm and Samsung Exynos baseband through USB, and generates a stream of GSMTAP packet (understandable by wireshark) containing cellular control plane messages.

#### Prerequisites
- **On Laptop:** 
```bash
sudo apt update
sudo apt install adb
git clone https://github.com/fgsect/scat

#Python 3.7 is a minimum requirement.
sudo apt install -y python3-venv python3-pip
python3 -m venv ~/venvs/scat
source ~/venvs/scat/bin/activate
python -m pip install -U pip wheel
python -m pip install "signalcat[fastcrc]"
```

- **On Phone:** 
	- Only works with Qualcomm or Samsung Exynos phones.
	- Enter Developer mode: **Settings** -> **About phone** -> tap **Build** number 7 times.
	- **System** -> **Developer Options** -> **USB Debugging** and **Rooted Debugging**
		**NOTE**: *If Rooted Debugging is not available, you have to root the phone.
  - Enter in DIAG mode, it's device specific procedure. For Fairphone5 and most Qualcomm devices: ([See other phones](https://band.radio/diag))
	- `adb devices`: Show list of devices connected to the laptop with their IDs.
	- `adb -s IDPhone root`: Run adb as root.
	- `adb -s IDPhone shell`: Open shell on your Android device.
		- `setprop sys.usb.config diag,serial_cdev,rmnet,dpl,qdss,adb` : Enter DIAG mode in the phone. This lets us access baseband debugging interfaces.
		- `exit`
     
**NOTE**: If you are using Quectel module, you just have to correctly set it up as documented in [this document](./quectel/index.md).

#### Usage
- **On Laptop**:
```bash
source ~/venvs/scat/bin/activate

#For Quectel Modules:
sudo -E ~/venvs/scat/bin/scat -t qc -s /dev/ttyUSB0 --pcap quectel.pcap
wireshark -X lua_script:../wireshark/scat.lua -r quectel.pcap

#For regular phones:
lsusb
#Example output: Bus 001 Device 061: ID 05c6:90db Qualcomm, Inc. FP5.
sudo -E ~/venvs/scat/bin/scat -t qc -u -a 001:061 -i 0 --pcap phone.pcap
wireshark -X lua_script:../wireshark/scat.lua -r phone.pcap
```

- `-t`: `qc` for Qualcomm and `sec` for Samsung. As FairPhone 5 has Qualcomm chip we will use `qc`.
- `-a`: Bus and Device IDs we got from `lsusb`. (001 and 061)
- `-i`: interface number of the diagnostic node.
- `--pcap`: put the logs in a pcap file to open it using **Wireshark**.
- `Ctrl + C`: Stop
- `wireshark -X lua_script:../wireshark/scat.lua -r phone.pcap`:  Open the .pcap file using wireshark, note that  scat.lua should be used so wireshark can understand 5G packets.

#### NOTES
1. Samsung phones with **No** Exynos chip are not supported.
2. Wireshark 3.3.0 or above is required for 5G packets.




### [Scrpy](https://github.com/Genymobile/scrcpy/blob/69858c6f437b1bfece96bc291c607de842837d36/doc/linux.md)
This tool allows screen mirroring and control a smartphone from your computer.
You should enable USB Debugging at your phone.
On your computer you have to download the latest version from their git repository.
Then: 
- `tar -xzf scrcpy-linux-x86_64-v3.2.tar.gz`
- `cd scrcpy-linux-x86_64-v3.2/`
- `./scrcpy`
- `./scrcpy -s R52XA01Q0EM`: if you have more than one device connected. you can get the ID of devices using `adb devices`.
- Click allow on the phone.


