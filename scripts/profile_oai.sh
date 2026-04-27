#!/bin/bash
################################################################################
# profile_oai.sh — CPU & Thermal Profiler for OAI nr-softmodem on ARM64
#
# PURPOSE: Continuously profile the nr-softmodem process on the Raspberry Pi 5
#          to capture the SIMDE translation overhead and thermal throttling
#          effects that occur during intensive LDPC coding/decoding operations.
#
# WHY:     The Pi 5 runs ARM64 but OAI is compiled with x86 AVX instructions
#          that must be emulated via SIMDE at runtime. This causes:
#            - Non-native execution of LDPC decoder inner loops
#            - Elevated memory bandwidth pressure on the RP1 USB/PCIe bridge
#            - CPU core saturation at much lower throughput than native x86
#
# OUTPUT:  /var/log/oai/cpu_profile.csv — CSV of per-core CPU utilization,
#          memory usage, ARM frequency, and system load, every 2 seconds.
#
# USAGE:   sudo ./profile_oai.sh
#          After test: import cpu_profile.csv into Python/matplotlib to
#          visualize the exact moment LDPC decoding saturated the ARM cores.
#
# EXIT:    Clean exit on SIGTERM/SIGINT; outputs final CSV row before exit.
#
# NOTES:   The script auto-re-finds nr-softmodem PID if it restarts during
#          the test run. Per-core CPU % is computed from /proc/stat deltas.
################################################################################

set -u

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

LOG_DIR="/var/log/oai"
CSV_OUTPUT="${LOG_DIR}/cpu_profile.csv"
PROFILE_INTERVAL=2          # seconds between samples
NR_PROCESS_NAME="nr-softmodem"

# Number of CPU cores (detect at startup)
N_CORES=$(nproc 2>/dev/null || echo 4)

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

get_nrsoftmodem_pid() {
    pgrep -x "${NR_PROCESS_NAME}" 2>/dev/null | head -n 1
}

get_cpu_temperature() {
    vcgencmd measure_temp 2>/dev/null | sed 's/temp=//' | sed 's/'\''C//'
}

get_arm_frequency_mhz() {
    local freq
    freq=$(vcgencmd measure_clock arm 2>/dev/null | sed 's/.*=//')
    if [[ -n "${freq}" && "${freq}" =~ ^[0-9]+$ ]]; then
        echo "scale=0; ${freq}/1000000" | bc
    else
        echo "N/A"
    fi
}

get_memory_usage_kb() {
    local pid="$1"
    if [[ -f "/proc/${pid}/status" ]]; then
        grep -E "^VmRSS:" "/proc/${pid}/status" 2>/dev/null | awk '{print $2}'
    else
        echo "0"
    fi
}

get_memory_total_kb() {
    awk '/^MemTotal:/ {print $2}' /proc/meminfo
}

get_memory_available_kb() {
    awk '/^MemAvailable:/ {print $2}' /proc/meminfo
}

get_load_average() {
    cat /proc/loadavg
}

# ─────────────────────────────────────────────────────────────────────────────
# CPU PERCENT CALCULATION
# ─────────────────────────────────────────────────────────────────────────────
# Compute per-core CPU utilization by reading /proc/stat twice (interval
# apart) and calculating the delta. Format:
#   cpu  user nice system idle iowait irq softirq steal guest guest_nice
#
# We compute: (total_time - idle_time) / total_time * 100 = CPU utilization %
# We also track per-core stats in /proc/stat for each core: cpu0, cpu1, ...

read_cpu_stats() {
    # Returns all cpuN lines (core-specific) and the aggregate cpu line
    grep '^cpu' /proc/stat
}

compute_cpu_percent() {
    local stats_before="$1"
    local stats_after="$2"
    local core="$3"  # e.g., "cpu0" or "cpu"

    # Extract the line for the requested core from both snapshots
    local line_before
    line_before=$(echo "${stats_before}" | grep "^${core} " | head -n 1)
    local line_after
    line_after=$(echo "${stats_after}" | grep "^${core} " | head -n 1)

    if [[ -z "${line_before}" || -z "${line_after}" ]]; then
        echo "-1"
        return
    fi

    # Fields: user nice system idle iowait irq softirq steal guest guest_nice guest_nice
    # We sum all non-idle fields as "active", and total as "total"
    local user_before nice_before system_before idle_before iowait_before irq_before softirq_before
    local user_after nice_after system_after idle_after iowait_after irq_after softirq_after

    user_before=$(echo "${line_before}" | awk '{print $2}')
    nice_before=$(echo "${line_before}" | awk '{print $3}')
    system_before=$(echo "${line_before}" | awk '{print $4}')
    idle_before=$(echo "${line_before}" | awk '{print $5}')
    iowait_before=$(echo "${line_before}" | awk '{print $6}')
    irq_before=$(echo "${line_before}" | awk '{print $7}')
    softirq_before=$(echo "${line_before}" | awk '{print $8}')

    user_after=$(echo "${line_after}" | awk '{print $2}')
    nice_after=$(echo "${line_after}" | awk '{print $3}')
    system_after=$(echo "${line_after}" | awk '{print $4}')
    idle_after=$(echo "${line_after}" | awk '{print $5}')
    iowait_after=$(echo "${line_after}" | awk '{print $6}')
    irq_after=$(echo "${line_after}" | awk '{print $7}')
    softirq_after=$(echo "${line_after}" | awk '{print $8}')

    local active_before=$((user_before + nice_before + system_before + iowait_before + irq_before + softirq_before))
    local active_after=$((user_after + nice_after + system_after + iowait_after + irq_after + softirq_after))
    local idle_delta=$((idle_after - idle_before))
    local active_delta=$((active_after - active_before))
    local total_delta=$((active_delta + idle_delta))

    if (( total_delta == 0 )); then
        echo "0.0"
    else
        echo "scale=1; ${active_delta} * 100 / ${total_delta}" | bc
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# CSV SETUP
# ─────────────────────────────────────────────────────────────────────────────

setup_csv() {
    if [[ ! -d "${LOG_DIR}" ]]; then
        mkdir -p "${LOG_DIR}"
        chmod 755 "${LOG_DIR}"
    fi

    # Build CSV header dynamically based on detected core count
    local header="timestamp,pid,active_cpus,load_avg,memory_rss_mb,memory_total_mb,memory_avail_mb,temp_c,arm_freq_mhz"
    local i
    for (( i=0; i<N_CORES; i++ )); do
        header="${header},cpu${i}_pct"
    done

    if [[ ! -f "${CSV_OUTPUT}" ]]; then
        echo "${header}" > "${CSV_OUTPUT}"
        chmod 644 "${CSV_OUTPUT}"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# LOG ROTATION CHECK
# ─────────────────────────────────────────────────────────────────────────────

check_log_size() {
    local size
    size=$(stat -f%z "${CSV_OUTPUT}" 2>/dev/null || stat -c%s "${CSV_OUTPUT}" 2>/dev/null)
    # Rotate if larger than 100 MB
    if [[ "${size}" -gt 104857600 ]]; then
        local rotated="${CSV_OUTPUT}.$(date +%Y%m%d_%H%M%S).gz"
        gzip -c "${CSV_OUTPUT}" > "${rotated}"
        echo "" > "${CSV_OUTPUT}"
        echo "CSV rotated to ${rotated}" >> "${LOG_DIR}/profile_watchdog.log" 2>/dev/null
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN PROFILING LOOP
# ─────────────────────────────────────────────────────────────────────────────

profile_loop() {
    local iteration=0
    local pid=""

    while true; do
        ((iteration++))

        # ── 1. Find nr-softmodem PID (auto-refind on respawn) ────────────
        pid=$(get_nrsoftmodem_pid)
        if [[ -z "${pid}" ]]; then
            # nr-softmodem not running yet — log wait state and skip this cycle
            echo "$(date '+%Y-%m-%dT%H:%M:%S'),no_proc,0,$(get_load_average),0,0,0,N/A,N/A" \
                >> "${CSV_OUTPUT}"
            sleep "${PROFILE_INTERVAL}"
            continue
        fi

        # ── 2. Read /proc/stat before sleep ──────────────────────────────
        local stats_before
        stats_before=$(read_cpu_stats)

        # ── 3. Sleep for interval (collects delta for accurate CPU %) ────
        sleep "${PROFILE_INTERVAL}"

        # ── 4. Read /proc/stat after sleep ───────────────────────────────
        local stats_after
        stats_after=$(read_cpu_stats)

        # ── 5. Collect all metrics ─────────────────────────────────────────
        local timestamp
        timestamp=$(date '+%Y-%m-%dT%H:%M:%S')

        local load_avg
        load_avg=$(get_load_average)

local mem_rss_kb mem_total_kb mem_avail_kb
    mem_rss_kb=$(get_memory_usage_kb "${pid}")
    mem_total_kb=$(get_memory_total_kb)
    mem_avail_kb=$(get_memory_available_kb)

    local mem_rss_mb
    mem_rss_mb=$(echo "scale=2; ${mem_rss_kb} / 1024" | bc 2>/dev/null || echo "0")
    local mem_total_mb
    mem_total_mb=$(echo "scale=2; ${mem_total_kb} / 1024" | bc 2>/dev/null || echo "0")
    local mem_avail_mb
    mem_avail_mb=$(echo "scale=2; ${mem_avail_kb} / 1024" | bc 2>/dev/null || echo "0")

    # Handle 'N/A' gracefully in bc arithmetic
    if [[ "${mem_rss_mb}" == "N/A" || "${mem_rss_mb}" == "0" && "${mem_rss_kb}" == "0" ]]; then
        mem_rss_mb="0"
    fi
    if [[ "${mem_total_mb}" == "N/A" || "${mem_total_mb}" == "0" && "${mem_total_kb}" == "0" ]]; then
        mem_total_mb="0"
    fi
    if [[ "${mem_avail_mb}" == "N/A" || "${mem_avail_mb}" == "0" && "${mem_avail_kb}" == "0" ]]; then
        mem_avail_mb="0"
    fi

        local temp arm_freq
        temp=$(get_cpu_temperature)
        arm_freq=$(get_arm_frequency_mhz)

        # ── 6. Compute per-core CPU percentages ──────────────────────────
        local core_pcts=""
        local c
        local total_active=0

        for (( c=0; c<N_CORES; c++ )); do
            local pct
            pct=$(compute_cpu_percent "${stats_before}" "${stats_after}" "cpu${c}")
            if [[ -z "${pct}" || "${pct}" == "-1" ]]; then
                pct="0.0"
            fi
            core_pcts="${core_pcts},${pct}"
            # Count cores with >80% usage as "active" (under stress)
            local pct_int
            pct_int=$(echo "${pct}" | awk '{print int($1)}')
            if (( pct_int >= 80 )); then
                ((total_active++))
            fi
        done

        # ── 7. Write CSV row ──────────────────────────────────────────────
        local row="${timestamp},${pid},${total_active},${load_avg},${mem_rss_mb},${mem_total_mb},${mem_avail_mb},${temp},${arm_freq}${core_pcts}"
        echo "${row}" >> "${CSV_OUTPUT}"

        # ── 8. Log rotation check (every 100 rows) ──────────────────────
        if (( iteration % 100 == 0 )); then
            check_log_size
        fi

    done
}

# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL HANDLING
# ─────────────────────────────────────────────────────────────────────────────

shutdown_profile() {
    echo "$(date '+%Y-%m-%dT%H:%M:%S'),SHUTDOWN,0,$(get_load_average),0,0,0,N/A,N/A" \
        >> "${CSV_OUTPUT}"
    exit 0
}

trap shutdown_profile SIGTERM SIGINT

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

setup_csv
echo "$(date '+%Y-%m-%dT%H:%M:%S'),INFO,Profiling started — N_CORES=${N_CORES}, interval=${PROFILE_INTERVAL}s" \
    >> "${CSV_OUTPUT}"

profile_loop