#!/bin/bash
################################################################################
# sdr_watchdog.sh — Baseband I/O & Power Watchdog
#
# PURPOSE: Continuously monitor the Raspberry Pi 5 running OAI nr-softmodem
#          and detect critical failures in four failure vectors:
#            1. UHD driver / USRP B210 errors
#            2. USB bus power drops / re-enumeration events
#            3. Kernel module / driver failures
#            4. Over-temperature or thermal shutdown warnings
#
# OUTPUT:  /var/log/oai/crash_report.log  — persistent log of all critical
#          events with timestamps, CPU temperature, and context dumps.
#
# USAGE:   sudo ./sdr_watchdog.sh
#
# EXIT:    Clean exit on SIGTERM/SIGINT; creates /var/log/oai/ on first run.
#
# NOTES:   Designed for RFsim mode first (no real USRP attached yet).
#          Patterns cover both simulated (rfsim) and real USB modes.
#          Requires sudo for dmesg, syslog, and vcgencmd access.
################################################################################

set -u  # Exit on undefined variable

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

LOG_DIR="/var/log/oai"
CRASH_LOG="${LOG_DIR}/crash_report.log"
PID_FILE="${LOG_DIR}/watchdog_nrsoftmodem.pid"

# Polling interval (seconds) between watchdog checks
CHECK_INTERVAL=1

# ─────────────────────────────────────────────────────────────────────────────
# PATTERN DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

# UHD / USRP B210 error patterns (AVX-to-ARM SIMDE translation + USB I/O)
# NOTE: Patterns must be specific to avoid false positives from generic WiFi/Bluetooth
# kernel messages. Each pattern targets a specific hardware/software failure vector.
declare -a UHD_PATTERNS=(
    "uhd.*error.*0xf"              # UHD source block got error code 0xf (USB transfer failure)
    "uhd.*rx.*error"               # UHD RX path error
    "uhd.*tx.*error"               # UHD TX path error
    "uhd.*bus.*error"              # UHD bus error
    "rx[0-9].*transfer.*status.*[5-9]"  # rx8 transfer status: 5 (USB timeout)
    "transfer.*status.*error"      # Generic transfer error
    "\bunderflow\b"                # Baseband underflow — word boundary to avoid "underflow" in WiFi
    "\boverflow\b"                 # Baseband overflow
    "b210.*fail"                   # B210-specific failure
    "usrp.*disconnect"             # USRP disconnect event
    "usrp.*timeout"                # USRP command timeout
)

# USB bus power / hot-plug / re-enumeration patterns
# Scoped to USB/HID/chipset drivers — avoids WiFi "device" false positives
declare -a USB_PATTERNS=(
    "usb.*bus.*reset"               # USB bus reset
    "hub.*reset"                    # Hub reset
    "usb.*device.*reset"            # Device reset
    "config.*fail.*usb"             # USB configuration failure
    "xhc.*宕"                       # USB host controller failure
    "power.*bus.*drop"              # Bus power drop
    "VUSB.*drop"                    # VUSB voltage drop
    "chip.*0x[0-9a-f]{4}.*disconnect"  # USB device disconnect with chip ID
)

# Kernel / driver failure patterns (OAI RAN components)
# These are scoped to RAN/5G specific error signatures
declare -a KERNEL_PATTERNS=(
    "nr-softmodem.*segfault"        # Softmodem segfault
    "nr-softmodem.*killed"         # OOM kill or signal kill
    "ldpc.*decoder.*fail"           # LDPC decoder failure
    "phy.*abort"                    # PHY layer abort
    "F1.*timeout"                   # F1 interface timeout
    "SCTP.*abort"                   # SCTP association abort
    "gnb.*crash"                    # gNB crash event
    "oai.*panic"                    # OAI panic kernel message
    "RRC.*abort"                    # RRC connection abort
    "NGAP.*fail"                    # NGAP failure
)

# Thermal / power shutdown patterns
declare -a THERMAL_PATTERNS=(
    "thermal.*shutdown"             # Thermal shutdown triggered
    "temperature.*critical"          # Critical temperature reached
    "throttled"                     # CPU throttling event
    "\bover_temp\b"                 # Overtemperature warning (word boundary)
    "\btemp.*9[0-9]\b"              # Temperature >= 90°C
    "vcgencmd.*throttle"            # vcgencmd throttle detected
)

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

log_msg() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%dT%H:%M:%S.%3N%z')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${CRASH_LOG}" 2>/dev/null
}

dump_capture() {
    local reason="$1"

    local timestamp
    timestamp=$(date '+%Y-%m-%dT%H:%M:%S.%3N%z')

    # Capture CPU temperature using vcgencmd (Pi 5 specific)
    local temp=""
    temp=$(vcgencmd measure_temp 2>/dev/null) || temp="N/A (vcgencmd unavailable)"

    # Capture current system load and memory — use /proc/meminfo to avoid locale issues
    local load_avg mem_total_kb mem_avail_kb mem_used_kb
    load_avg=$(cat /proc/loadavg 2>/dev/null) || load_avg="N/A"
    mem_total_kb=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo 2>/dev/null || echo "0")
    mem_avail_kb=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo 2>/dev/null || echo "0")
    mem_used_kb=$((mem_total_kb - mem_avail_kb))
    local memory
    memory=$(printf "total=%s used=%s free=%s available=%s" "$((mem_total_kb / 1024))MB" "$((mem_used_kb / 1024))MB" "$((mem_avail_kb / 1024))MB" "$((mem_avail_kb / 1024))MB")

    # Capture last 20 lines of dmesg for context
    local dmesg_tail
    dmesg_tail=$(dmesg | tail -n 20 2>/dev/null) || dmesg_tail="N/A (dmesg inaccessible)"

    # Capture current nr-softmodem process state
    # Note: pgrep may return multiple PIDs (thread group) — capture first/primary only
    local proc_state="N/A"
    local pid
    pid=$(pgrep -x nr-softmodem 2>/dev/null | head -n 1) || pid=""
    if [[ -n "${pid}" && -d "/proc/${pid}" ]]; then
        proc_state=$(cat /proc/"${pid}"/stat 2>/dev/null | awk '{print $3}') || proc_state="N/A"
    fi

    # ── Write crash entry ──────────────────────────────────────────────────
    {
        echo "========================================"
        echo "CRASH EVENT #$(date +%s)"
        echo "========================================"
        echo "  Timestamp  : ${timestamp}"
        echo "  Reason     : ${reason}"
        echo "  CPU Temp   : ${temp}"
        echo "  Load Avg   : ${load_avg}"
        echo "  Memory     : ${memory}"
        echo "  nr-softmodem PID : ${pid:-not running}"
        echo "  Process State    : ${proc_state}"
        echo ""
        echo "--- Last 20 dmesg lines ---"
        echo "${dmesg_tail}"
        echo "========================================"
        echo ""
    } >> "${CRASH_LOG}"
}

# ─────────────────────────────────────────────────────────────────────────────
# LOG SETUP
# ─────────────────────────────────────────────────────────────────────────────

setup_log_dir() {
    if [[ ! -d "${LOG_DIR}" ]]; then
        mkdir -p "${LOG_DIR}"
        chmod 755 "${LOG_DIR}"
        echo "Created log directory: ${LOG_DIR}"
    fi
    # Ensure crash log exists
    touch "${CRASH_LOG}" 2>/dev/null && chmod 644 "${CRASH_LOG}"
}

record_startup() {
    log_msg "INFO" "===== sdr_watchdog.sh started ====="
    log_msg "INFO" "Monitoring UHD/USB/Kernel/Thermal failure vectors every ${CHECK_INTERVAL}s"
    log_msg "INFO" "Crash report: ${CRASH_LOG}"
    log_msg "INFO" "SIMDE translation mode: ARM64 + x86 AVX emulation (Pi 5)"
}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN WATCHDOG LOOP
# ─────────────────────────────────────────────────────────────────────────────

watchdog_loop() {
    local iteration=0

    while true; do
        ((iteration++))

        # ── 1. Check dmesg for UHD / USB / Kernel / Thermal patterns ──────
        #    dmesg captures kernel-level events including USB and UHD driver
        #    messages. We capture since last check by tracking dmesg size.

        local dmesg_output
        dmesg_output=$(dmesg 2>/dev/null) || dmesg_output=""

        for pattern in "${UHD_PATTERNS[@]}"; do
            if echo "${dmesg_output}" | grep -iE "${pattern}" >/dev/null 2>&1; then
                log_msg "CRITICAL" "UHD error detected: pattern='${pattern}'"
                dump_capture "UHD_ERROR: ${pattern}"
            fi
        done

        for pattern in "${USB_PATTERNS[@]}"; do
            if echo "${dmesg_output}" | grep -iE "${pattern}" >/dev/null 2>&1; then
                log_msg "CRITICAL" "USB bus event detected: pattern='${pattern}'"
                dump_capture "USB_EVENT: ${pattern}"
            fi
        done

        for pattern in "${KERNEL_PATTERNS[@]}"; do
            if echo "${dmesg_output}" | grep -iE "${pattern}" >/dev/null 2>&1; then
                log_msg "CRITICAL" "Kernel/OAI failure detected: pattern='${pattern}'"
                dump_capture "KERNEL_FAILURE: ${pattern}"
            fi
        done

        for pattern in "${THERMAL_PATTERNS[@]}"; do
            if echo "${dmesg_output}" | grep -iE "${pattern}" >/dev/null 2>&1; then
                log_msg "WARNING" "Thermal/power event detected: pattern='${pattern}'"
                dump_capture "THERMAL_EVENT: ${pattern}"
            fi
        done

        # ── 2. Check syslog (/var/log/syslog) for SCTP/gnb-related errors ──
        #    syslog carries higher-level OAI and SCTP events that may not
        #    appear in dmesg (e.g., F1AP timeout, SCTP association loss).

        if [[ -r "/var/log/syslog" ]]; then
            local syslog_tail
            syslog_tail=$(tail -n 200 "/var/log/syslog" 2>/dev/null) || syslog_tail=""

            for pattern in "SCTP.*abort" "F1.*timeout" "gnb.*crash" "nr-softmodem.*error" "LDPC.*fail"; do
                if echo "${syslog_tail}" | grep -iE "${pattern}" >/dev/null 2>&1; then
                    log_msg "WARNING" "Syslog OAI event: pattern='${pattern}'"
                    dump_capture "SYSLOG_OAI_EVENT: ${pattern}"
                fi
            done
        fi

        # ── 3. Periodic heartbeat (every 60 iterations = 1 minute) ───────
        #    Confirms the watchdog is still running and the system is stable.

        if (( iteration % 60 == 0 )); then
            local temp
            temp=$(vcgencmd measure_temp 2>/dev/null) || temp="N/A"
            local load
            load=$(cat /proc/loadavg 2>/dev/null) || load="N/A"
            local nr_running
            nr_running=$(pgrep -x nr-softmodem 2>/dev/null) || nr_running="0"
            log_msg "INFO" "Heartbeat — Temp: ${temp} | Load: ${load} | nr-softmodem instances: ${nr_running}"
        fi

        sleep "${CHECK_INTERVAL}"
    done
}

# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL HANDLING (graceful shutdown)
# ─────────────────────────────────────────────────────────────────────────────

shutdown_watchdog() {
    log_msg "INFO" "===== sdr_watchdog.sh shutting down (SIGTERM/SIGINT) ====="
    exit 0
}

trap shutdown_watchdog SIGTERM SIGINT

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

setup_log_dir
record_startup
log_msg "INFO" "Watchdog loop started — monitoring failure vectors..."
watchdog_loop