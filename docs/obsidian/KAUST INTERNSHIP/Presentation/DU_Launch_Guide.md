# Launch DU on Raspberry Pi 5 with USRP B210

## Step 1: Connect to serber-pi

```bash
sshpass -p 'root4SERBER' ssh -o StrictHostKeyChecking=no serber@10.85.42.8
```

## Step 2: Verify USRP is detected

```bash
uhd_find_devices
```

Expected output:
```
[INFO] UHD 4.8.0.HEAD
[INFO] Connected to USRP B210 (serial: 35F8ABA)
```

## Step 3: Navigate to OAI directory

```bash
cd ~/oai-du
```

## Step 4: Set library path

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/openairinterface5g/cmake_targets/ran_build/build
```

## Step 5: Run DU with USRP B210 config (24 PRB)

```bash
sudo ./nr-softmodem -O ~/gnb-du.sa.band78.24prb.usrpb210.conf --thread-pool 1 -g 2
```

## Quick Reference

| Action | Command |
|--------|---------|
| Connect to serber-pi | `sshpass -p 'root4SERBER' ssh serber@10.85.42.8` |
| Check USRP detection | `uhd_find_devices` |
| Navigate to OAI | `cd ~/oai-du` |
| Run DU with USRP | `sudo ./nr-softmodem -O ~/gnb-du.sa.band78.24prb.usrpb210.conf --thread-pool 1 -g 2` |
| Stop DU | `Ctrl+C` |

## Expected Output

```
CMDLINE: "./nr-softmodem" "-O" "/home/serber/gnb-du.sa.band78.24prb.usrpb210.conf" ...
[GNB_APP] F1AP: gNB idx 0 gNB_DU_id 1, gNB_DU_name gNB-Pi5-24PRB-DU
[GNB_APP] Configured DU: cell ID 12345678, PCI 0
[USRP] Opening B210 (serial: 35F8ABA) ...
[USRP] Setting master clock to 30.72 MHz
[USRP] Tune TX: 3.6 GHz
[USRP] Tune RX: 3.6 GHz
```

## Notes

- **Do NOT** use `--rfsim` flag when using real USRP hardware
- The config `gnb-du.sa.band78.24prb.usrpb210.conf` is configured for:
  - Band n78 (3.5 GHz)
  - 24 PRB (~10 MHz bandwidth)
  - USRP B210 with serial 35F8ABA
- Run with `sudo` to enable real-time priority and memory locking