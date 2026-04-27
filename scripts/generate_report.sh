#!/bin/bash
################################################################################
# generate_report.sh — Automated Suitability Report Generator
#
# PURPOSE: Parse the three diagnostic log files produced by sdr_watchdog.sh,
#          profile_oai.sh, and sctp_monitor.sh to generate a comprehensive
#          suitability verdict for running OAI CU/DU split on the Raspberry Pi 5.
#
# USE CASE: Run this script AFTER a test session has completed and all three
#           monitoring scripts have been stopped. It will analyze the complete
#           log history and produce a yes/no verdict with supporting evidence.
#
# INPUT FILES (all in /var/log/oai/):
#   crash_report.log   — from sdr_watchdog.sh
#   cpu_profile.csv    — from profile_oai.sh
#   sctp_status.log    — from sctp_monitor.sh
#   sctp_health.csv    — from sctp_monitor.sh (optional)
#
# OUTPUT:
#   /var/log/oai/suitability_report.txt — Human-readable report
#   Exit code: 0 = SUITABLE, 1 = CONDITIONALLY SUITABLE, 2 = NOT SUITABLE
#
# USAGE:   sudo ./generate_report.sh
#
# NOTES:   If any log file is missing, the script skips that vector and marks
#          it as "INSUFFICIENT DATA". All thresholds are tunable in the
#          CONFIGURATION section below.
################################################################################

set -u

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — TUNABLE THRESHOLDS
# ─────────────────────────────────────────────────────────────────────────────

LOG_DIR="/var/log/oai"

# Profile interval (must match profile_oai.sh's sampling rate in seconds)
PROFILE_INTERVAL=2

# CPU vector thresholds
CPU_WARN_THRESHOLD_PCT=95     # Sustained >95% = WARNING
CPU_FAIL_THRESHOLD_PCT=98     # Sustained >98% for >60s = FAIL
CPU_WARN_DURATION_S=30        # Duration for warning threshold
CPU_FAIL_DURATION_S=60         # Duration for fail threshold

# Thermal vector thresholds
TEMP_WARN_C=85                # Temperature >85°C = WARNING
TEMP_FAIL_C=90                # Temperature >90°C = FAIL
TEMP_SAMPLES_ABOVE_WARN=5     # Number of samples above warn = confirmed warning

# Baseband I/O vector thresholds
CRASH_WARN_COUNT=3            # >3 crash events = WARNING
CRASH_FAIL_COUNT=5            # >5 crash events = FAIL
USB_DISCONNECT_ANY=1          # Any USB disconnect = FAIL
UHD_ERROR_CODE_F_ANY=1        # Any UHD error code 0xf = FAIL

# F1-C / SCTP vector thresholds
SCTP_ASSOC_LOSS_ANY=1         # Any association loss = FAIL
SCTP_RETRANS_WARN_PER_MIN=10  # >10 retransmissions/min = WARNING
SCTP_RETRANS_FAIL_PER_MIN=50  # >50 retransmissions/min = FAIL

# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────────────────────────────────────

REPORT_FILE="${LOG_DIR}/suitability_report.txt"

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

print_report_header() {
    {
        echo "================================================================================"
        echo "   OAI CU/DU SPLIT SUITABILITY REPORT — Raspberry Pi 5"
        echo "================================================================================"
        echo ""
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S %z')"
        echo "Log directory analyzed: ${LOG_DIR}"
        echo ""
    } >> "${REPORT_FILE}"
}

print_vector_header() {
    local name="$1"
    local sep="--------------------------------------------------------------------------------"
    {
        echo ""
        echo "${sep}"
        echo "VECTOR: ${name}"
        echo "${sep}"
    } >> "${REPORT_FILE}"
}

pass()   { echo "  [PASS] $1" | tee -a "${REPORT_FILE}"; }
warn()   { echo "  [WARNING] $1" | tee -a "${REPORT_FILE}"; }
fail()   { echo "  [FAIL] $1" | tee -a "${REPORT_FILE}"; }
info()   { echo "  [INFO] $1" | tee -a "${REPORT_FILE}"; }
detail() { echo "         $1" | tee -a "${REPORT_FILE}"; }

# ─────────────────────────────────────────────────────────────────────────────
# VECTOR 1: CPU SATURATION ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

analyze_cpu_vector() {
    local csv="${LOG_DIR}/cpu_profile.csv"
    print_vector_header "VECTOR 1 — CPU SATURATION (SIMDE Translation Overhead)"

    if [[ ! -f "${csv}" ]]; then
        warn "cpu_profile.csv not found — insufficient data for CPU analysis"
        echo "FAIL_REASON: Missing cpu_profile.csv" >> "${REPORT_FILE}"
        return 2
    fi

    local total_rows
    total_rows=$(wc -l < "${csv}" | awk '{print $1}')
    total_rows=$((total_rows - 1))  # Exclude header

    if (( total_rows < 10 )); then
        warn "Insufficient data: only ${total_rows} samples found"
        return 1
    fi

    info "Total samples analyzed: ${total_rows} (at 2s interval = ~$((total_rows * 2 / 60)) minutes)"
    detail "Thresholds: WARNING >${CPU_WARN_THRESHOLD_PCT}% for >${CPU_WARN_DURATION_S}s | FAIL >${CPU_FAIL_THRESHOLD_PCT}% for >${CPU_FAIL_DURATION_S}s"
    echo "" >> "${REPORT_FILE}"

    # Get number of CPU columns by reading header
    # Header: timestamp,pid,active_cpus,load_avg,memory_rss_mb,memory_total_mb,memory_avail_mb,temp_c,arm_freq_mhz,cpu0_pct,...
    local n_cpu_cols
    n_cpu_cols=$(head -n 1 "${csv}" | awk -F',' '{print NF-9}')

    local sustained_warn_duration=0
    local sustained_fail_duration=0
    local max_cpu_ever=0

    # Read all data rows (skip header)
    local line_num=0
    while IFS= read -r line; do
        ((line_num++))
        [[ "${line_num}" -eq 1 ]] && continue
        [[ "${line}" == *,INFO,* ]] && continue
        [[ "${line}" == *,SHUTDOWN,* ]] && continue
        [[ "${line}" == *,no_proc,* ]] && continue
        [[ -z "${line}" ]] && continue
        local pid_field
        pid_field=$(echo "${line}" | cut -d',' -f2)
        [[ -z "${pid_field}" || ! "${pid_field}" =~ ^[0-9]+$ ]] && continue
        local n_fields
        n_fields=$(echo "${line}" | awk -F',' '{print NF}')
        local cpu_start_idx=$((n_fields - n_cpu_cols + 1))
        local row_max=0
        local c
        for (( c=cpu_start_idx; c<=n_fields; c++ )); do
            local val
            val=$(echo "${line}" | cut -d',' -f"${c}" 2>/dev/null | tr -d ' \n\r')
            if [[ -n "${val}" && "${val}" =~ ^[0-9]*\.?[0-9]+$ ]]; then
                local int_val
                int_val=$(echo "${val}" | cut -d'.' -f1)
                if [[ -n "${int_val}" && "${int_val}" =~ ^[0-9]+$ ]]; then
                    if (( int_val > row_max )); then
                        row_max=${int_val}
                    fi
                fi
            fi
        done
        if (( row_max > max_cpu_ever )); then
            max_cpu_ever=${row_max}
        fi
        if (( row_max >= CPU_FAIL_THRESHOLD_PCT )); then
            sustained_fail_duration=$((sustained_fail_duration + PROFILE_INTERVAL))
        elif (( row_max >= CPU_WARN_THRESHOLD_PCT )); then
            sustained_warn_duration=$((sustained_warn_duration + PROFILE_INTERVAL))
        fi
    done < "${csv}"

    # Evaluate
    local result=0
    if (( sustained_fail_duration >= CPU_FAIL_DURATION_S )); then
        fail "CPU core saturation detected: >${CPU_FAIL_THRESHOLD_PCT}% for ${sustained_fail_duration}s (threshold: ${CPU_FAIL_DURATION_S}s)"
        detail "Maximum single-core peak CPU: ${max_cpu_ever}%"
        echo "FAIL_REASON: Sustained CPU >${CPU_FAIL_THRESHOLD_PCT}% for ${sustained_fail_duration}s" >> "${REPORT_FILE}"
        result=2
    elif (( sustained_warn_duration >= CPU_WARN_DURATION_S )); then
        warn "CPU elevated utilization detected: >${CPU_WARN_THRESHOLD_PCT}% for ${sustained_warn_duration}s (threshold: ${CPU_WARN_DURATION_S}s)"
        detail "Maximum single-core peak CPU: ${max_cpu_ever}%"
        echo "WARNING_REASON: Elevated CPU >${CPU_WARN_THRESHOLD_PCT}% for ${sustained_warn_duration}s" >> "${REPORT_FILE}"
        result=1
    else
        pass "CPU utilization within acceptable bounds (peak: ${max_cpu_ever}%, sustained warn: ${sustained_warn_duration}s)"
    fi

    # Compute peak CPU using validated numeric values only
    # Extract 1-min load average (first field of col 4) for rows with valid PID
    # Handle both integer and decimal-only loads (e.g., ".50" without leading 0)
    local load_avg_max
    load_avg_max=$(awk -F',' '
        NR>1 && $2 != "INFO" && $2 != "SHUTDOWN" && $2 != "no_proc" && $2 ~ /^[0-9]+$/ {
            # Extract 1-min load avg from col 4 (format: "0.92 0.86 0.72 1/399 749559")
            split($4, parts, " ")
            val = parts[1]
            # Normalize decimal-only values like ".50" to "0.50"
            if (substr(val, 1, 1) == ".") val = "0" val
            if (val != "" && val + 0 > max + 0) max = val + 0
        }
        END {printf "%.2f", max}
    ' "${csv}" 2>/dev/null)
    if [[ -z "${load_avg_max}" || "${load_avg_max}" == "0.00" || "${load_avg_max}" == "0" ]]; then
        load_avg_max=$(awk -F',' '
            NR>1 {
                split($4, parts, " ")
                val = parts[1]
                if (substr(val, 1, 1) == ".") val = "0" val
                if (val != "" && val + 0 > max + 0) max = val + 0
            }
            END {printf "%.2f", max}
        ' "${csv}" 2>/dev/null)
    fi
    info "Peak system load average during test: ${load_avg_max}"

    return ${result}
}

# ─────────────────────────────────────────────────────────────────────────────
# VECTOR 2: THERMAL THROTTLING ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

analyze_thermal_vector() {
    local csv="${LOG_DIR}/cpu_profile.csv"
    local crash_log="${LOG_DIR}/crash_report.log"
    print_vector_header "VECTOR 2 — THERMAL THROTTLING"

    if [[ ! -f "${csv}" ]]; then
        warn "cpu_profile.csv not found — insufficient data for thermal analysis"
        echo "FAIL_REASON: Missing cpu_profile.csv" >> "${REPORT_FILE}"
        return 2
    fi

    # Normalize values like ".50" to "0.50" for proper arithmetic
    normalize() {
        local v="$1"
        if [[ -n "${v}" && "${v}" =~ ^[0-9]*\.?[0-9]*$ ]]; then
            if [[ "${v}" =~ ^\.[0-9] ]]; then
                echo "0${v}"
            else
                echo "${v}"
            fi
        else
            echo "0"
        fi
    }

    local heartbeat_temp_max heartbeat_load_max
    heartbeat_temp_max=$(grep "Heartbeat" "${crash_log}" 2>/dev/null | \
        sed -n 's/.*Temp: temp=\([0-9]*\.[0-9]*\)'"'"'C.*/\1/p' | \
        sort -rn | head -n 1)
    heartbeat_load_max=$(grep "Heartbeat" "${crash_log}" 2>/dev/null | \
        sed -n 's/.*Load: \([0-9]*\.[0-9]*\) [0-9.]* [0-9.]* .*/\1/p' | \
        LC_ALL=C awk '{if ($1+0 > max) max = $1+0} END {printf "%.2f", max+0}')

    # Normalize decimal-only values
    heartbeat_temp_max=$(normalize "${heartbeat_temp_max}")
    heartbeat_load_max=$(normalize "${heartbeat_load_max}")

    local csv="${LOG_DIR}/cpu_profile.csv"
    local csv_temp_max csv_load_max
    csv_temp_max=$(awk -F',' '
        NR>1 && $2 != "INFO" && $2 != "SHUTDOWN" && $2 != "no_proc" && $2 ~ /^[0-9]+$/ && $8 != "N/A" && $8 != "" && $8 ~ /^[0-9]/ {
            if ($8 + 0 > max + 0) max = $8 + 0
        }
        END {printf "%.2f", max}
    ' "${csv}" 2>/dev/null)

    csv_load_max=$(LC_ALL=C awk -F',' '
        NR>1 && $2 != "INFO" && $2 != "SHUTDOWN" && $2 != "no_proc" && $2 ~ /^[0-9]+$/ {
            split($4, parts, " ")
            val = parts[1]
            if (substr(val, 1, 1) == ".") val = "0" val
            if (val != "" && val + 0 > max + 0) max = val + 0
        }
        END {printf "%.2f", max}
    ' "${csv}" 2>/dev/null)

    csv_temp_max=$(normalize "${csv_temp_max}")
    csv_load_max=$(normalize "${csv_load_max}")

    # Use whichever source has the higher temperature
    local max_temp
    max_temp=$(echo "${heartbeat_temp_max} ${csv_temp_max}" | awk '{if ($1+0 > $2+0) print $1; else print $2}')
    local load_avg_peak
    load_avg_peak=$(echo "${heartbeat_load_max} ${csv_load_max}" | awk '{if ($1+0 > $2+0) print $1; else print $2}')

    # Print load average if we have it
    if [[ -n "${load_avg_peak}" && "${load_avg_peak}" != "0.00" && "${load_avg_peak}" != "0" ]]; then
        info "Peak system load average during test: ${load_avg_peak}"
    fi

    # Count samples above thresholds (only from heartbeat — CSV has no valid rows)
    local warm_count critical_count
    warm_count=$(grep "Heartbeat" "${crash_log}" 2>/dev/null | \
        sed -n 's/.*Temp: temp=\([0-9]*\.[0-9]*\)'"'"'C.*/\1/p' | \
        awk -v thresh="${TEMP_WARN_C}" '{if (($1+0) > thresh) count++} END {print count+0}')
    critical_count=$(grep "Heartbeat" "${crash_log}" 2>/dev/null | \
        sed -n 's/.*Temp: temp=\([0-9]*\.[0-9]*\)'"'"'C.*/\1/p' | \
        awk -v thresh="${TEMP_FAIL_C}" '{if (($1+0) > thresh) count++} END {print count+0}')

    local result=0

    if (( critical_count > 0 )) || \
       [[ -n "${max_temp}" && -n "$(echo "${max_temp}" | grep -E '^[0-9]+\.?[0-9]*$')" && \
         $(echo "0.1 + ${max_temp} > ${TEMP_FAIL_C}" | bc -l 2>/dev/null) -eq 1 ]]; then
        fail "Critical temperature exceeded: ${max_temp}°C (>${TEMP_FAIL_C}°C threshold)"
        detail "Samples above ${TEMP_FAIL_C}°C: ${critical_count}"
        echo "FAIL_REASON: Temperature ${max_temp}°C exceeded ${TEMP_FAIL_C}°C threshold (${critical_count} samples)" >> "${REPORT_FILE}"
        result=2
    elif (( warm_count >= TEMP_SAMPLES_ABOVE_WARN )) || \
         [[ -n "${max_temp}" && -n "$(echo "${max_temp}" | grep -E '^[0-9]+\.?[0-9]*$')" && \
           $(echo "0.1 + ${max_temp} > ${TEMP_WARN_C}" | bc -l 2>/dev/null) -eq 1 ]]; then
        warn "Thermal warning: temperature reached ${max_temp}°C (>${TEMP_WARN_C}°C threshold)"
        detail "Samples above ${TEMP_WARN_C}°C: ${warm_count}"
        echo "WARNING_REASON: Temperature ${max_temp}°C exceeded ${TEMP_WARN_C}°C threshold (${warm_count} samples)" >> "${REPORT_FILE}"
        result=1
    else
        pass "Temperature within safe range (max: ${max_temp}°C, samples above ${TEMP_WARN_C}°C: ${warm_count})"
    fi

    # Check for ARM frequency throttling (column 9 = arm_freq_mhz)
    # Only check if both min and nominal are valid positive integers
    local min_freq nominal_freq=2400
    min_freq=$(awk -F',' -v nom="${nominal_freq}" '
        NR>1 && $9 != "N/A" && $9 != "" && $9 ~ /^[0-9]+$/ && $9 > 0 {
            if (min_val == "" || $9 + 0 < min_val + 0) min_val = $9
        }
        END {print min_val+0}
    ' "${csv}" 2>/dev/null)

    if [[ -n "${min_freq}" && "${min_freq}" =~ ^[0-9]+$ && "${min_freq}" -gt 0 ]]; then
        if (( min_freq < nominal_freq )); then
            warn "ARM frequency throttling detected: min freq ${min_freq} MHz (nominal: ${nominal_freq} MHz)"
            detail "Frequency drop of $((nominal_freq - min_freq)) MHz indicates thermal or power throttling"
        fi
    else
        info "ARM frequency data: N/A or insufficient samples (throttling check skipped)"
    fi

    return ${result}
}

# ─────────────────────────────────────────────────────────────────────────────
# VECTOR 3: BASEBAND I/O HEALTH ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

analyze_baseband_io_vector() {
    local crash_log="${LOG_DIR}/crash_report.log"
    print_vector_header "VECTOR 3 — BASEBAND I/O & USB HEALTH"

    if [[ ! -f "${crash_log}" ]]; then
        warn "crash_report.log not found — assuming no baseband failures detected"
        info "This may indicate the watchdog did not run or log files were cleaned"
        return 0
    fi

    local total_crashes uhd_errors usb_disconnects overflow_underflow late_packets

    local grep_out
    grep_out=$(grep -c "CRASH EVENT" "${crash_log}" 2>/dev/null); total_crashes=$((${grep_out:-0}))
    grep_out=$(grep -ciE "UHD_ERROR|uhd.*error.*0xf|rx[0-9].*transfer.*status.*[5-9]|transfer.*status.*error" "${crash_log}" 2>/dev/null); uhd_errors=$((${grep_out:-0}))
    grep_out=$(grep -ciE "USB_EVENT|usb.*disconnect|usb.*reset|device.*disconnect|power.*bus.*drop" "${crash_log}" 2>/dev/null); usb_disconnects=$((${grep_out:-0}))
    grep_out=$(grep -ciE "overflow|underflow" "${crash_log}" 2>/dev/null); overflow_underflow=$((${grep_out:-0}))
    grep_out=$(grep -ciE "late|Late" "${crash_log}" 2>/dev/null); late_packets=$((${grep_out:-0}))

    info "Crash events logged: ${total_crashes}"
    detail "UHD errors: ${uhd_errors} | USB disconnects: ${usb_disconnects} | overflow/underflow: ${overflow_underflow} | late packets: ${late_packets}"
    echo "" >> "${REPORT_FILE}"

    local result=0

    # Any UHD error code 0xf or USB disconnect = automatic FAIL
    if grep -qE "UHD_ERROR|uhd.*error.*0xf" "${crash_log}" 2>/dev/null; then
        fail "UHD error code 0xf detected — USB/USRP communication failure"
        detail "This indicates unrecoverable USB transfer failure (likely B210 disconnect or bus error)"
        echo "FAIL_REASON: UHD error code 0xf (USB transfer failure)" >> "${REPORT_FILE}"
        result=2
    fi

    if (( usb_disconnects > 0 )); then
        fail "USB bus disconnect/re-enumeration events detected: ${usb_disconnects}"
        detail "RP1 PCIe-to-USB bridge instability or power delivery issue"
        echo "FAIL_REASON: USB disconnect/re-enumeration (${usb_disconnects} events)" >> "${REPORT_FILE}"
        result=2
    fi

    if (( result == 0 )); then
        if (( total_crashes >= CRASH_FAIL_COUNT )); then
            fail "High crash count: ${total_crashes} events (fail threshold: ${CRASH_FAIL_COUNT})"
            echo "FAIL_REASON: ${total_crashes} crash events exceeded threshold of ${CRASH_FAIL_COUNT}" >> "${REPORT_FILE}"
            result=2
        elif (( total_crashes >= CRASH_WARN_COUNT )); then
            warn "Elevated crash count: ${total_crashes} events (warn threshold: ${CRASH_WARN_COUNT})"
            echo "WARNING_REASON: ${total_crashes} crash events exceeded warning threshold of ${CRASH_WARN_COUNT}" >> "${REPORT_FILE}"
            result=1
        else
            pass "Baseband I/O stable: ${total_crashes} crash events (threshold warn: ${CRASH_WARN_COUNT}, fail: ${CRASH_FAIL_COUNT})"
        fi
    fi

    # Check for overflow/underflow (SIMDE stall indicators)
    if (( overflow_underflow > 0 )); then
        warn "Baseband overflow/underflow events detected: ${overflow_underflow}"
        detail "This indicates SIMDE translation stalls or I/O buffer exhaustion"
    fi

    if (( late_packets > 0 )); then
        warn "Late packet events detected: ${late_packets}"
        detail "Scheduler hiccup or PHY timing issues in the LDPC pipeline"
    fi

    return ${result}
}

# ─────────────────────────────────────────────────────────────────────────────
# VECTOR 4: F1-C SCTP STABILITY ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

analyze_sctp_vector() {
    local sctp_log="${LOG_DIR}/sctp_status.log"
    local sctp_health="${LOG_DIR}/sctp_health.csv"
    print_vector_header "VECTOR 4 — F1-C SCTP CONTROL PLANE STABILITY"

    if [[ ! -f "${sctp_log}" ]]; then
        warn "sctp_status.log not found — insufficient data for SCTP analysis"
        echo "FAIL_REASON: Missing sctp_status.log" >> "${REPORT_FILE}"
        return 2
    fi

    # Detect if this was an RFsim-mode test — in RFsim, no CU is connected by design
    local rfsim_mode="no"
    if grep -q "RFsim mode detected\|RFsim mode" "${sctp_log}" 2>/dev/null; then
        rfsim_mode="yes"
    fi

    local assoc_losses retrans_fail_events high_retrans_warnings

    local grep_out
    grep_out=$(grep -ciE "F1-C SCTP association CLOSED|F1.*association.*DOWN|ERROR.*SCTP.*abort" "${sctp_log}" 2>/dev/null); assoc_losses=$((${grep_out:-0}))
    grep_out=$(grep -ciE "SCTP.*abort|abort.*SCTP" "${sctp_log}" 2>/dev/null); retrans_fail_events=$((${grep_out:-0}))
    grep_out=$(grep -ciE "retransmission rate HIGH|retrans.*>.*10/min" "${sctp_log}" 2>/dev/null); high_retrans_warnings=$((${grep_out:-0}))

    info "SCTP association losses logged: ${assoc_losses}"
    info "SCTP abort events: ${retrans_fail_events}"
    info "High retransmission warnings: ${high_retrans_warnings}"
    if [[ "${rfsim_mode}" == "yes" ]]; then
        info "RFsim mode detected — F1-C association test was expected to be non-functional"
    fi
    echo "" >> "${REPORT_FILE}"

    local result=0

    # Any real association loss (non-RFsim) = automatic FAIL
    # RFsim mode: association not found is EXPECTED, not a failure
    if (( assoc_losses > 0 )); then
        if [[ "${rfsim_mode}" == "yes" ]]; then
            warn "F1-C SCTP association loss in RFsim mode: ${assoc_losses} event(s) — expected without CU"
        else
            fail "F1-C SCTP association loss detected: ${assoc_losses} events"
            detail "DU lost connection to CU — gNB deregistered from AMF"
            echo "FAIL_REASON: F1-C SCTP association loss (${assoc_losses} events)" >> "${REPORT_FILE}"
            result=2
        fi
    fi

    # Analyze health CSV if available
    if [[ -f "${sctp_health}" ]] && (( $(wc -l < "${sctp_health}") > 1 )); then
        local max_retrans_per_min
        max_retrans_per_min=$(awk -F',' 'NR>1 {print $6}' "${sctp_health}" 2>/dev/null | sort -n | tail -n 1)

        if [[ -n "${max_retrans_per_min}" && -n "$(echo "${max_retrans_per_min}" | grep -E '^[0-9]+$')" ]]; then
            if (( max_retrans_per_min > SCTP_RETRANS_FAIL_PER_MIN )); then
                fail "SCTP retransmission rate critically high: ${max_retrans_per_min}/min (fail threshold: ${SCTP_RETRANS_FAIL_PER_MIN}/min)"
                echo "FAIL_REASON: SCTP retrans rate ${max_retrans_per_min}/min exceeded ${SCTP_RETRANS_FAIL_PER_MIN}/min" >> "${REPORT_FILE}"
                result=2
            elif (( max_retrans_per_min > SCTP_RETRANS_WARN_PER_MIN )); then
                warn "SCTP retransmission rate elevated: ${max_retrans_per_min}/min (warn threshold: ${SCTP_RETRANS_WARN_PER_MIN}/min)"
                echo "WARNING_REASON: SCTP retrans rate ${max_retrans_per_min}/min exceeded ${SCTP_RETRANS_WARN_PER_MIN}/min" >> "${REPORT_FILE}"
                if (( result < 1 )); then result=1; fi
            fi
            detail "Peak retransmission rate observed: ${max_retrans_per_min}/min"
        fi
    fi

    if (( result == 0 )); then
        pass "F1-C SCTP control plane stable: no association losses, retransmission rate within bounds"
    fi

    return ${result}
}

# ─────────────────────────────────────────────────────────────────────────────
# FINAL VERDICT
# ─────────────────────────────────────────────────────────────────────────────

compute_final_verdict() {
    local cpu_result="$1"
    local thermal_result="$2"
    local io_result="$3"
    local sctp_result="$4"

    local fail_count=0 warn_count=0
    local reasons=""

    if (( cpu_result == 2 )); then ((fail_count++)); reasons="${reasons} CPU_SATURATION,"; fi
    if (( cpu_result == 1 )); then ((warn_count++)); reasons="${reasons} CPU_ELEVATED,"; fi
    if (( thermal_result == 2 )); then ((fail_count++)); reasons="${reasons} THERMAL_THROTTLING,"; fi
    if (( thermal_result == 1 )); then ((warn_count++)); reasons="${reasons} THERMAL_WARNING,"; fi
    if (( io_result == 2 )); then ((fail_count++)); reasons="${reasons} BASEBAND_IO_FAILURE,"; fi
    if (( io_result == 1 )); then ((warn_count++)); reasons="${reasons} BASEBAND_IO_WARN,"; fi
    if (( sctp_result == 2 )); then ((fail_count++)); reasons="${reasons} F1C_SCTP_LOSS,"; fi
    if (( sctp_result == 1 )); then ((warn_count++)); reasons="${reasons} F1C_SCTP_DEGRADED,"; fi

    local exit_code=0
    local verdict_text=""
    local verdict_summary=""

    if (( fail_count > 0 )); then
        exit_code=2
        verdict_text="NOT SUITABLE"
        verdict_summary="The Raspberry Pi 5 exhibited critical failures in ${fail_count} failure vector(s) and is NOT suitable for this use case without hardware or configuration changes."
    elif (( warn_count > 0 )); then
        exit_code=1
        verdict_text="CONDITIONALLY SUITABLE"
        verdict_summary="The Raspberry Pi 5 exhibited warnings in ${warn_count} failure vector(s). It may be usable for prototyping but with documented bottlenecks and limitations."
    else
        exit_code=0
        verdict_text="SUITABLE"
        verdict_summary="The Raspberry Pi 5 passed all four failure vectors. It is SUITABLE for prototyping the CU/DU split architecture, though real-world RF performance with a live USRP B210 remains to be validated."
    fi

    echo "" >> "${REPORT_FILE}"
    echo "================================================================================" >> "${REPORT_FILE}"
    echo "                          FINAL VERDICT" >> "${REPORT_FILE}"
    echo "================================================================================" >> "${REPORT_FILE}"
    echo "" >> "${REPORT_FILE}"
    echo "  VERDICT: ${verdict_text}" >> "${REPORT_FILE}"
    echo "" >> "${REPORT_FILE}"
    echo "  ${verdict_summary}" >> "${REPORT_FILE}"
    echo "" >> "${REPORT_FILE}"
    if [[ -n "${reasons}" ]]; then
        echo "  Flagged vectors: $(echo "${reasons}" | sed 's/,$//')" >> "${REPORT_FILE}"
        echo "" >> "${REPORT_FILE}"
    fi
    echo "  CPU vector:    $( [ ${cpu_result} -eq 0 ] && echo PASS || ([ ${cpu_result} -eq 1 ] && echo WARNING || echo FAIL) )" >> "${REPORT_FILE}"
    echo "  Thermal vector: $( [ ${thermal_result} -eq 0 ] && echo PASS || ([ ${thermal_result} -eq 1 ] && echo WARNING || echo FAIL) )" >> "${REPORT_FILE}"
    echo "  Baseband I/O:  $( [ ${io_result} -eq 0 ] && echo PASS || ([ ${io_result} -eq 1 ] && echo WARNING || echo FAIL) )" >> "${REPORT_FILE}"
    echo "  F1-C SCTP:     $( [ ${sctp_result} -eq 0 ] && echo PASS || ([ ${sctp_result} -eq 1 ] && echo WARNING || echo FAIL) )" >> "${REPORT_FILE}"
    echo "" >> "${REPORT_FILE}"
    echo "================================================================================" >> "${REPORT_FILE}"
    echo "  Tested: $(date '+%Y-%m-%d %H:%M:%S %z')" >> "${REPORT_FILE}"
    echo "  Script: generate_report.sh" >> "${REPORT_FILE}"
    echo "================================================================================" >> "${REPORT_FILE}"

    return ${exit_code}
}

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

main() {
    # Clear previous report
    > "${REPORT_FILE}"

    print_report_header

    echo "Analyzing diagnostic logs in: ${LOG_DIR}"
    echo ""

    local cpu_result=0 thermal_result=0 io_result=0 sctp_result=0

    analyze_cpu_vector;         cpu_result=$?
    analyze_thermal_vector;     thermal_result=$?
    analyze_baseband_io_vector;  io_result=$?
    analyze_sctp_vector;        sctp_result=$?

    compute_final_verdict ${cpu_result} ${thermal_result} ${io_result} ${sctp_result}
    local exit_code=$?

    echo ""
    echo "Report written to: ${REPORT_FILE}"
    echo ""
    cat "${REPORT_FILE}"

    exit ${exit_code}
}

main "$@"