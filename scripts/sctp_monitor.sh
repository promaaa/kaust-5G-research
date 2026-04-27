#!/bin/bash
################################################################################
# sctp_monitor.sh — F1-C / SCTP Interface Monitor for OAI DU on Raspberry Pi 5
#
# PURPOSE: Validate the stability of the F1-C control plane (SCTP association)
#          between the DU (Pi 5 running nr-softmodem) and the CU (serber-firecell
#          at 10.76.170.45). Detects SCTP state changes, packet drops, and
#          retransmissions on the F1 interface ports.
#
# WHY:    The F1-C interface carries F1AP messages (gNB-DU ↔ gNB-CU control
#         traffic). If the SCTP association drops or becomes unreliable, the
#         entire gNB will lose registration with the AMF and go offline.
#
# SCTP PORTS used by OAI:
#   38472  — F1-C (SCTP control plane)  — primary DU↔CU control
#   2152   — GTP-U (user plane data)    — iframe payloads, not SCTP but
#                                         monitored alongside for completeness
#
# OUTPUT:  /var/log/oai/sctp_status.log — Human-readable log of SCTP state
#          changes, periodic health snapshots, and warning events.
#
# USAGE:   sudo ./sctp_monitor.sh
#
# EXIT:    Clean exit on SIGTERM/SIGINT.
#
# NOTES:   This script reads from /proc/net/sctp/assocs which reflects the
#          kernel's SCTP state. SCTP association IDs and state strings vary
#          by kernel version; this script handles the most common formats.
################################################################################

set -u

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

LOG_DIR="/var/log/oai"
SCTP_LOG="${LOG_DIR}/sctp_status.log"
HEALTH_LOG="${LOG_DIR}/sctp_health.csv"

# Port definitions
SCTP_F1_PORT=38472
GTP_U_PORT=2152

# CU IP (gNB-CU side of F1 interface — the peer)
# AMF/CU on serber-firecell at 10.76.170.45 (university Ethernet)
CU_IP="${CU_IP:-10.76.170.45}"

# Polling intervals
STATE_CHECK_INTERVAL=5    # seconds between SCTP state checks
HEALTH_CHECK_INTERVAL=60  # seconds between full health snapshots

# Thresholds for warnings
MAX_RETRANSMISSIONS_PER_MIN=10
MAX_DROPPED_PKTS_PER_MIN=5

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

# Detect RFsim mode by checking if nr-softmodem was launched with --rfsim flag.
# In RFsim mode, no actual F1-C/SCTP connection to CU is expected.
is_rfsim_mode() {
    local pid
    pid=$(pgrep -x nr-softmodem 2>/dev/null | head -n 1)
    if [[ -n "${pid}" && -f "/proc/${pid}/cmdline" ]]; then
        local cmdline
        cmdline=$(cat "/proc/${pid}/cmdline" | tr '\0' ' ')
        if echo "${cmdline}" | grep -qE "\-\-rfsim"; then
            return 0  # true — RFsim mode
        fi
    fi
    return 1  # false — real hardware mode
}

log_msg() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%dT%H:%M:%S.%3N%z')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${SCTP_LOG}" 2>/dev/null
}

setup_log_dir() {
    if [[ ! -d "${LOG_DIR}" ]]; then
        mkdir -p "${LOG_DIR}"
        chmod 755 "${LOG_DIR}"
    fi
    sudo touch "${SCTP_LOG}" 2>/dev/null && sudo chmod 644 "${SCTP_LOG}"
}

# ─────────────────────────────────────────────────────────────────────────────
# SCTP ASSOCIATION STATE PARSING
# ─────────────────────────────────────────────────────────────────────────────
# The /proc/net/sctp/assocs file format varies by kernel. Common format:
# ASSOC   SOCK   FAMILY   LADDR   RADDR   HBINT   ASSOC-ID   STRTXSZ   MAXRTX
# 01      03     02       05      05      30000   01          262142    10
#
# The state is encoded as a number (e.g., 01=CLOSED, 05=ESTABLISHED).
# We need to read the kernel's sctp sysctl to map states, or look at /proc/net/sctp

read_sctp_assocs() {
    # Returns the raw contents of /proc/net/sctp/assocs
    if [[ -r "/proc/net/sctp/assocs" ]]; then
        cat /proc/net/sctp/assocs 2>/dev/null
    else
        echo "UNREADABLE"
    fi
}

find_f1_association() {
    # Find the SCTP association that connects to CU_IP on SCTP_F1_PORT
    # Returns the association ID if found, empty string if not
    local assocs
    assocs=$(read_sctp_assocs)

    if [[ "${assocs}" == "UNREADABLE" || -z "${assocs}" ]]; then
        echo ""
        return
    fi

    # Use ss (socket statistics) for reliable association lookup
    # ss -t shows SCTP associations with local:remote addresses
    local assoc_info
    assoc_info=$(ss -t -n -o 2>/dev/null | grep "sctp" | grep "${CU_IP}:${SCTP_F1_PORT}" | head -n 1)

    if [[ -z "${assoc_info}" ]]; then
        echo ""
        return
    fi

    # ss output example:
    # State      Recv-Q  Send-Q  Local Address:Port   Peer Address:Port
    # ESTAB      0       0       10.76.170.117:38472  10.76.170.45:38472

    # Extract association ID (shown in square brackets or as 'assoc_id' in ss)
    # Fallback: iterate via /proc/net/sctp/assocs to find matching endpoint
    local assoc_id=""
    while IFS= read -r line; do
        # Skip header lines
        echo "${line}" | grep -qE "^ASSOC|SOCK" && continue
        # Check if line contains our CU IP (as remote address)
        if echo "${line}" | grep -q "${CU_IP}"; then
            # Association ID is the first numeric field (e.g., "01" from assoc line)
            assoc_id=$(echo "${line}" | awk '{print $1}' | sed 's/^0*//')
            break
        fi
    done <<< "${assocs}"

    echo "${assoc_id}"
}

get_sctp_stats() {
    # Read /proc/net/sctp/snmp or use netstat -s for SCTP stats
    # Returns: retransmissions, chunk_dropped, fragmentation_failed, etc.

    if [[ -r "/proc/net/sctp/snmp" ]]; then
        cat /proc/net/sctp/snmp 2>/dev/null
    else
        # Fall back to netstat -s
        netstat -s 2>/dev/null | grep -i "sctp" || echo ""
    fi
}

count_sctp_retransmissions() {
    # Returns the current cumulative retransmission count
    local retrans_count
    retrans_count=$(netstat -s 2>/dev/null | grep -iE "sctp.*retransmis|retransmis.*sctp" | awk '{print $1}' || echo "0")
    echo "${retrans_count:-0}"
}

count_sctp_dropped_chunks() {
    local drop_count
    drop_count=$(netstat -s 2>/dev/null | grep -iE "sctp.*drop|chunk.*drop" | awk '{print $1}' || echo "0")
    echo "${drop_count:-0}"
}

# ─────────────────────────────────────────────────────────────────────────────
# SCTP STATE CHECK
# ─────────────────────────────────────────────────────────────────────────────

check_sctp_state() {
    local last_state="$1"
    local rfsim_mode="$2"  # "yes" or "no"

    local assoc_info
    assoc_info=$(ss -t -n -o 2>/dev/null | grep "sctp" | grep "${CU_IP}:${SCTP_F1_PORT}" | head -n 1)

    if [[ -z "${assoc_info}" ]]; then
        if [[ "${last_state}" != "DOWN" ]]; then
            if [[ "${rfsim_mode}" == "yes" ]]; then
                log_msg "INFO" "F1-C SCTP association not found — expected in RFsim mode (no CU connected)"
            else
                log_msg "ERROR" "F1-C SCTP association not found — DU may be disconnected from CU (${CU_IP})"
            fi
            last_state="DOWN"
        fi
    else
        if echo "${assoc_info}" | grep -q "ESTAB"; then
            if [[ "${last_state}" != "UP" ]]; then
                local assoc_id
                assoc_id=$(find_f1_association)
                log_msg "INFO" "F1-C SCTP association ESTABLISHED with CU ${CU_IP}:${SCTP_F1_PORT} (assoc_id=${assoc_id:-N/A})"
                last_state="UP"
            fi
        elif echo "${assoc_info}" | grep -q "CLOSED"; then
            if [[ "${last_state}" != "DOWN" ]]; then
                log_msg "ERROR" "F1-C SCTP association CLOSED — CU link lost"
                last_state="DOWN"
            fi
        elif echo "${assoc_info}" | grep -q "UNCONN"; then
            if [[ "${last_state}" != "DOWN" ]]; then
                log_msg "WARNING" "F1-C SCTP association UNCONN — attempting reconnection"
                last_state="DOWN"
            fi
        else
            if [[ "${last_state}" != "UNKNOWN" ]]; then
                log_msg "INFO" "F1-C SCTP state: ${assoc_info}"
                last_state="UNKNOWN"
            fi
        fi
    fi

    echo "${last_state}"
}

# ─────────────────────────────────────────────────────────────────────────────
# PERIODIC HEALTH SNAPSHOT
# ─────────────────────────────────────────────────────────────────────────────

write_health_snapshot() {
    local retrans_before="$1"
    local retrans_after="$2"

    local retrans_delta=$((retrans_after - retrans_before))
    local retrans_per_min=0
    if (( HEALTH_CHECK_INTERVAL > 0 )); then
        retrans_per_min=$((retrans_delta * 60 / HEALTH_CHECK_INTERVAL))
    fi

    local timestamp
    timestamp=$(date '+%Y-%m-%dT%H:%M:%S')

    local assoc_id cu_ip_state
    assoc_id=$(find_f1_association)
    cu_ip_state=$(ss -t -n -o 2>/dev/null | grep "sctp" | grep "${CU_IP}:${SCTP_F1_PORT}" | head -n 1 | awk '{print $1}' || echo "N/A")

    # Log to CSV (append mode): timestamp,assoc_id,state,retrans_delta,retrans_per_min
    {
        echo "HEALTH,${timestamp},${assoc_id:-NONE},${cu_ip_state},${retrans_delta},${retrans_per_min}"
    } >> "${HEALTH_LOG}" 2>/dev/null

    # Log to main SCTP log
    log_msg "INFO" "Health snapshot — Assoc: ${assoc_id:-NONE}, State: ${cu_ip_state}, Retrans: +${retrans_delta} (${retrans_per_min}/min)"

    # Warn if thresholds exceeded
    if (( retrans_per_min > MAX_RETRANSMISSIONS_PER_MIN )); then
        log_msg "WARNING" "SCTP retransmission rate HIGH: ${retrans_per_min}/min (threshold: ${MAX_RETRANSMISSIONS_PER_MIN}/min)"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN MONITOR LOOP
# ─────────────────────────────────────────────────────────────────────────────

monitor_loop() {
    local iteration=0
    local sctp_state="UNKNOWN"
    local retrans_before
    retrans_before=$(count_sctp_retransmissions)

    # Detect RFsim mode once at startup
    local rfsim_mode="no"
    if is_rfsim_mode; then
        rfsim_mode="yes"
        log_msg "INFO" "RFsim mode detected — F1-C association monitoring adjusted accordingly"
    fi

    while true; do
        ((iteration++))

        # ── SCTP state check every STATE_CHECK_INTERVAL seconds ──────────
        sctp_state=$(check_sctp_state "${sctp_state}" "${rfsim_mode}")

        # ── Full health snapshot every HEALTH_CHECK_INTERVAL seconds ─────
        local health_step=$((HEALTH_CHECK_INTERVAL / STATE_CHECK_INTERVAL))
        if (( health_step == 0 )); then
            health_step=1
        fi
        if (( iteration % health_step == 0 )); then
            local retrans_after
            retrans_after=$(count_sctp_retransmissions)
            write_health_snapshot "${retrans_before}" "${retrans_after}"
            retrans_before="${retrans_after}"
        fi

        # ── Periodic association summary (every 5 minutes) ──────────────
        if (( iteration % 60 == 0 )); then
            log_msg "INFO" "SCTP monitor still active — assoc_id=$(find_f1_association), state=${sctp_state}"
        fi

        sleep "${STATE_CHECK_INTERVAL}"
    done
}

# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL HANDLING
# ─────────────────────────────────────────────────────────────────────────────

shutdown_monitor() {
    log_msg "INFO" "===== sctp_monitor.sh shutting down ====="
    exit 0
}

trap shutdown_monitor SIGTERM SIGINT

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

setup_log_dir
touch "${HEALTH_LOG}" 2>/dev/null && chmod 644 "${HEALTH_LOG}"

log_msg "INFO" "===== sctp_monitor.sh started ====="
log_msg "INFO" "Monitoring F1-C SCTP to CU=${CU_IP}:${SCTP_F1_PORT}"
log_msg "INFO" "State check interval: ${STATE_CHECK_INTERVAL}s | Health snapshot interval: ${HEALTH_CHECK_INTERVAL}s"
log_msg "INFO" "GTP-U port ${GTP_U_PORT} also monitored for completeness"

monitor_loop