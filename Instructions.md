# 5G PWS PROCEDURE - SERBER-FIRECELL

==========================================
## BEFORE YOU START
==========================================

The USRP B210 must be plugged in. Check with:
```bash
sudo uhd_find_devices
```

If it says "No USRP Devices Found", the hardware is not connected properly.

==========================================
## START EVERYTHING (CN + gNB)
==========================================

Run these commands in order, one at a time:

### 1. Start Core Network (Docker containers)
```bash
cd ~/oai-cn5g
sudo docker-compose up -d
```
Wait 30 seconds. The "ims" container may fail - this is OK, it is not needed for 5G PWS.

### 2. Verify CN is running
```bash
sudo docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'oai-|mysql'
```
Expected output:
```
NAMES
oai-upf     Up ... (healthy)
oai-smf     Up ... (healthy)
oai-amf     Up ... (healthy)
oai-ausf    Up ... (healthy)
oai-udm     Up ... (healthy)
oai-udr     Up ... (healthy)
mysql       Up ... (healthy)
oai-nrf     Up ... (healthy)
```

### 3. Start gNB (5G Base Station)
```bash
cd ~/openairinterface5g/cmake_targets/ran_build/build
sudo ./nr-softmodem -O ~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf > /tmp/gnb.log 2>&1 &
```
Wait 25 seconds for gNB to start.

### 4. Check gNB is connected to AMF
```bash
sudo docker logs oai-amf --tail 20 2>&1 | grep -E 'gNB|Connected'
```
Expected: You should see "Connected" in the Status column for gNB.

### 5. Check gNB is transmitting
```bash
tail -20 /tmp/gnb.log
```
Expected: You should see "Frame.Slot" messages. If you see "No USRP Device Found", the USRP is not connected.

==========================================
## STOP EVERYTHING (CN + gNB)
==========================================

### Stop gNB
```bash
sudo pkill -9 nr-softmodem
```

### Stop CN (optional - containers can keep running)
```bash
cd ~/oai-cn5g
sudo docker-compose down
```
Note: "ims" container error is normal and can be ignored.

==========================================
## CHECK STATUS
==========================================

### Is gNB running?
```bash
ps aux | grep nr-softmodem | grep -v grep
```
Expected: Shows 3-4 processes (bash, sudo, nr-softmodem, helper). If empty, gNB is not running.

### Is gNB connected to AMF?
```bash
sudo docker logs oai-amf --tail 15 2>&1 | grep 'gNB'
```
Expected: Shows table with Status "Connected"

### Is gNB transmitting?
```bash
tail -5 /tmp/gnb.log
```
Expected: Shows "Frame.Slot X.X" messages, not errors.

### Any registered UEs (phones)?
```bash
sudo docker logs oai-amf --tail 20 2>&1 | grep -E 'UE|5GMM'
```
Expected: Shows UE table. Empty or "-" means no phones connected.

### Full AMF status
```bash
sudo docker logs oai-amf --tail 25 2>&1 | grep -E 'Status|gNB|UE|5GMM'
```

==========================================
## SEND PWS (PUBLIC WARNING) MESSAGE
==========================================

### 1. Edit the warning message
```bash
nano ~/openairinterface5g/sib8.conf
```
The file looks like this:
```
messageIdentifier=1112;
serialNumber=0000;
dataCodingScheme=48;
text=Firecell PWS test alert.|KUAR drone ready.;
mode=0;
```

Change the `text=` line. Use `|` to separate lines.
Example: `text=EMERGENCY ALERT.|This is a test.;`

Save: Ctrl+O, Enter, Ctrl+X

### 2. Trigger the warning to send
```bash
touch ~/openairinterface5g/sib8.conf
```
Wait 10 seconds.

### 3. Verify it was sent
```bash
tail -30 /tmp/gnb.log | grep -E 'SIB8|warning|segment|Write Replace'
```
Expected: Shows "[SIB8]" messages and "MAC received Write Replace Warning Request"

==========================================
## VIEW SIB8 CONFIG
==========================================
```bash
cat ~/openairinterface5g/sib8.conf
```

==========================================
## CONNECT PHONE
==========================================

1. Enable 5G on Nothing Phone:
   - Settings → Mobile Network → Preferred Network Type → 5G

2. Phone should automatically find PLMN 001.01 cell

3. Check if phone registered:
```bash
sudo docker logs oai-amf --tail 20 2>&1 | grep -E 'UE|5GMM'
```
Look for IMSI 001010000059453

==========================================
## TECHNICAL DETAILS
==========================================

| Item | Value |
|------|-------|
| gNB IP | 192.168.70.140 |
| AMF IP | 192.168.70.132 |
| PLMN | 001.01 |
| TAC | 1 |
| Cell ID | 12345678 |
| Frequency | 3619.2 MHz (Band 78) |
| Bandwidth | 106 PRB (20 MHz) |
| UE IMSI | 001010000059453 |

## File Locations
| File | Path |
|------|------|
| gNB binary | ~/openairinterface5g/cmake_targets/ran_build/build/nr-softmodem |
| gNB config | ~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf |
| SIB8 config | ~/openairinterface5g/sib8.conf |
| gNB log | /tmp/gnb.log |
| CN config | ~/oai-cn5g/docker-compose.yaml |