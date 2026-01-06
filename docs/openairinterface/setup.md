# OpenAirInterface – Baseline Setup

This document describes the **baseline setup** of an OpenAirInterface (OAI) 5G Standalone system.

> **NOTE**
>
> An alternative setup that integrates the system with a custom **Network Management System (NMS)** is documented separately in:
>
> - `docs/openairinterface/nms-setup.md`
>
> The baseline setup presented here is a **prerequisite** for the NMS-based deployment.

## Requirements
The minimum requirements to run the system are:
- Laptop/Desktop for OAI **CN5G** and OAI **gNB**
    - Operating System: Ubuntu 24.04 LTS
    - CPU: 8 cores x86_64 @ 3.5 GHz
    - RAM: 32 GB
- Software Defined Radio ([USRP B210](https://www.ettus.com/all-products/ub210-kit/), [USRP N300](https://www.ettus.com/all-products/USRP-N300/) or [USRP X300](https://www.ettus.com/all-products/x300-kit/))
- Smartphone that supports 5G

## Core Network Setup
### pre-requisites

```
sudo apt install -y git net-tools putty

# https://docs.docker.com/engine/install/ubuntu/
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your username to the docker group, otherwise you will have to run in sudo mode.
sudo usermod -a -G docker $(whoami)
reboot
```

### Docker files

Download and copy configuration files:
```
wget -O ~/oai-cn5g.zip https://gitlab.eurecom.fr/oai/openairinterface5g/-/archive/develop/openairinterface5g-develop.zip?path=doc/tutorial_resources/oai-cn5g
unzip ~/oai-cn5g.zi p
mv ~/openairinterface5g-develop-doc-tutorial_resources-oai-cn5g/doc/tutorial_resources/oai-cn5g ~/oai-cn5g
rm -r ~/openairinterface5g-develop-doc-tutorial_resources-oai-cn5g ~/oai-cn5g.zip
```

Pull docker images
```
cd ~/oai-cn5g
docker compose pull
```


### Start/Stop Core Network

Start:
```
cd ~/oai-cn5g
docker compose up -d
```

Stop:
```
cd ~/oai-cn5g
docker compose down
```

### Configure Network Functions

The config file `config.yaml` is located at `~/oai-cn5g/conf` and contains the configuration parameters for all the network functions.  Here you can modify the list of supported **PLMN**, integrity and  encryption algorithms, and other parameters.

In addition to this, you can update the database of the system by modifying the `oai_db.sql` file inside `~/oai-cn5g/database`. For instance, in order to add new users (sim cards) to the system, you would have to write the following sql query:
```
INSERT INTO `AuthenticationSubscription` (`ueid`, `authenticationMethod`, `encPermanentKey`, `protectionParameterId`, `sequenceNumber`, `authenticationManagementField`, `algorithmId`, `encOpcKey`, `encTopcKey`, `vectorGenerationInHss`, `n5gcAuthMethod`, `rgAuthenticationInd`, `supi`) VALUES
    ('001010000059449', '5G_AKA', '5686e601f3a1942d4c5cd262ba6b4b20', '5686e601f3a1942d4c5cd262ba6b4b20', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'aeb1cabd8ed7a09b48d17eb3d8af172c', NULL, NULL, NULL, NULL, '001010000059449');
```
You only have to modify the values of `ueid, encPermanentKey, protectionParameterId, encOpcKey, supi`  based on your sim card parameters.

**NOTE**: The configuration file and the database must be updated **before starting the containers**.

## gNB Setup
### Build UHD from source:
```
sudo apt install -y autoconf automake build-essential ccache cmake cpufrequtils doxygen ethtool g++ git inetutils-tools libboost-all-dev libncurses-dev libusb-1.0-0 libusb-1.0-0-dev libusb-dev python3-dev python3-mako python3-numpy python3-requests python3-scipy python3-setuptools python3-ruamel.yaml

git clone https://github.com/EttusResearch/uhd.git ~/uhd
cd ~/uhd
git checkout v4.8.0.0
cd host
mkdir build
cd build
cmake ../
make -j $(nproc)
make test # This step is optional
sudo make install
sudo ldconfig
sudo uhd_images_downloader
```

To check if uhd driver was successfully installed, run this command:
```
sudo uhd_find_devices
```
It should show the SDR you are using. 
You may need to unplug the SDR then re-plug it.

### Build gNB
```
# Get openairinterface5g source code
git clone https://gitlab.eurecom.fr/oai/openairinterface5g.git ~/openairinterface5g
cd ~/openairinterface5g
git checkout develop

# Install OAI dependencies
cd ~/openairinterface5g/cmake_targets
sudo ./build_oai -I

# Build OAI gNB
cd ~/openairinterface5g/cmake_targets
sudo ./build_oai -w USRP --ninja --gNB -C
```
### Run gNB
```
cd ~/openairinterface5g/cmake_targets/ran_build/build
sudo ./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf -E --continuous-tx
```
Check `~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/` to choose the correct config file based on your SDR and your desired configuration. Additionally  you can modify the config file by changing the PLMN transmitted by the gNB, frequency used, supported algorithms and other parameters.

