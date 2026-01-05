# Building Drivers for NVIDIA Jetson

This guide walks through building and installing USB drivers (CDC-WDM, CDC-MBIM, QMI-WWAN) for the NVIDIA Jetson device.

Your running kernel may not include certain drivers by default. Rather than downloading pre-compiled drivers (which often won't work due to version mismatches), we'll compile them from source to match your exact kernel configuration.

## Step 1: Check Which Drivers Are Missing

```bash
zcat /proc/config.gz 2>/dev/null | egrep 'CONFIG_USB_WDM|QMI_WWAN|CONFIG_USB_NET_CDC_MBIM'
```

If you see lines like:
```
# CONFIG_USB_NET_CDC_MBIM is not set
# CONFIG_USB_NET_QMI_WWAN is not set
# CONFIG_USB_WDM is not set
```

These drivers are not currently enabled.

---

## Step 2: Check the installed kernel

```bash
uname -r
```

Example output: `5.15.148-tegra`

Check your release version:

```bash
cat /etc/nv_tegra_release
```

Example output: `R36 (release), REVISION: 4.7`

Or

```bash
dpkg -l | grep -E 'nvidia-l4t-kernel|nvidia-l4t-core' | head -n 20
```

## Step 3: Download the Kernel Source

The required kernel source must be obtained from NVIDIA and should match your currently running version.
Minor patch differences (e.g., source `36.4.4` vs kernel `36.4.7`) may work, but this is **not guaranteed**.

Download the **Public Sources** (`Driver Package (BSP) Sources`) archive for your release from the official NVIDIA documentation:

[https://developer.nvidia.com/embedded/jetson-linux-archive](https://developer.nvidia.com/embedded/jetson-linux-archive)


This will download a file similar to:

```
public_sources.tbz2
```

### Extract the Kernel Source

```bash
mkdir -p ~/kernel-src
cd ~/kernel-src

# Extract NVIDIA public sources
tar xf ~/Downloads/public_sources.tbz2

cd Linux_for_Tegra/source/

# Extract kernel-related source archives
tar xf kernel_src.tbz2
tar xf nvidia_kernel_display_driver_source.tbz2
tar xf kernel_oot_modules_src.tbz2
sudo apt install build-essential bc

# Enter the kernel source tree
cd kernel/kernel-jammy-src
```

---

## Step 4: Copy Your Running Kernel's Configuration

```bash
zcat /proc/config.gz > .config
```

This ensures your new modules will be compatible with your running kernel.

## Step 5: Update Configuration with Defaults

```bash
make olddefconfig
```

This command:
- Takes your existing `.config`
- Adds any new configuration options with default values

## Step 6: Verify Kernel Version

```bash
make kernelrelease
```

Should show something like: `5.15.148`

Compare with your running kernel:
```bash
uname -r
```

The base version should match (minor suffix differences like `-tegra` are usually okay).

## Step 7: Enable Required Drivers

First, install ncurses if needed:
```bash
sudo apt update
sudo apt install libncurses-dev
```

Then open the configuration menu:
```bash
make menuconfig
```

Navigate and enable these drivers as **modules** (press `M` to set):

1. **USB_WDM**:
   - `Device Drivers` → `USB support` → `USB Wireless Device Management support` → Press `M` → Press `Esc` twice to go back

2. **USB_NET_CDC_MBIM**:
   - `Device Drivers` → `Network device support` → `USB Network Adapters` → `CDC MBIM support` → Press `M` → `QMI WWAN driver for Qualcomm MSM based 3G and LTE modems` → Press `M`

Save and exit (press `Esc` until prompted, then select `Yes`).

### Process dependencies

```bash
make olddefconfig
```

### Verify the Configuration

```bash
grep -E 'CONFIG_USB_WDM|QMI_WWAN|CONFIG_USB_NET_CDC_MBIM' .config
```

Should show:
```
CONFIG_USB_NET_CDC_MBIM=m
CONFIG_USB_NET_QMI_WWAN=m
CONFIG_USB_WDM=m
```

## Step 8: Prepare for Module Building

```bash
make modules_prepare
```

This sets up the build environment and generates necessary headers for module compilation.

## Step 9: Build the Drivers

Build only the specific directories containing our drivers:

```bash
# Build USB class drivers (includes cdc-wdm)
make M=drivers/usb/class

# Build USB network drivers (includes cdc_mbim, qmi_wwan)
make M=drivers/net/usb
```

## Step 10: Install the Modules

```bash
sudo make M=drivers/usb/class modules_install
sudo make M=drivers/net/usb modules_install
```

This installs modules to `/lib/modules/5.15.148/updates/`

## Step 11: Copy Modules to Correct Location (if needed)

If the modules were installed to a different kernel version directory than your running kernel:

```bash
# Check where modules were installed
ls /lib/modules/

# If installed to 5.15.148 but running 5.15.148-tegra, copy them:
sudo cp -r /lib/modules/5.15.148/updates /lib/modules/5.15.148-tegra/
```

## Step 12: Update Module Dependencies

```bash
sudo depmod -a 5.15.148-tegra
```

Replace `5.15.148-tegra` with your actual kernel version from `uname -r`.

## Step 13: Load the Modules

```bash
sudo modprobe cdc-wdm
sudo modprobe cdc_mbim
```

### Verify modules are loaded
```bash
lsmod | grep -E 'cdc_wdm|cdc_mbim|qmi'
```
It should show either qmi or mbmi driver, depending on what the quectel is using.

## Step 14: Test with Your Modem

Check if quectel modem is detected:

```bash
# Check USB devices
lsusb

# Check for cdc-wdm device
ls /dev/cdc-wdm*

# Check for network interface
ip link show wwan0
```


---
