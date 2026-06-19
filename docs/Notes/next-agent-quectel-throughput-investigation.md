# Prompt: Investigate Why Caged Quectel Backhaul Reaches 42 Mbps

You are taking over a validated OAI CU/DU lab where the caged Quectel F1 backhaul unexpectedly measured about 42 Mbps on a Nothing Phone, while earlier Ethernet CU/DU split runs were closer to 23 Mbps. Do not assume Quectel is inherently faster; determine why the measured end-to-end phone throughput improved.

Context:
- Canonical deployment repo: `/Users/promaa/Documents/oai-cu-du-lab`
- Research repo/report: `/Users/promaa/Documents/kaust-5G-research`
- Latest validated caged evidence: `/Users/promaa/Documents/oai-cu-du-lab/experiments/20260613_092358_caged_quectel_f1_backhaul_start`
- Latest code commit with TUI fixes: `ec0f9e2 Harden caged Quectel launch validation`
- The PASS run proved:
  - firecell donor gNB served the Quectel modem
  - minipc access DU served the phone with PCI 0/TAC 1/Cell ID `12345678L`
  - F1-C and F1-U were on `wg-quectel-f1`
  - WireGuard outer UDP was on live Quectel `wwan0`
  - management Ethernet/WiFi did not carry minipc F1

Goal:
Explain why caged Quectel backhaul now gives about 42 Mbps while Ethernet split previously gave about 23 Mbps, and identify whether the improvement comes from radio/access conditions, OAI launch state, scheduler/MCS behavior, CPU timing, packet path, MTU/tunnel behavior, or measurement methodology.

Work plan:
1. Compare sanitized evidence from the 42 Mbps caged Quectel run against the best Ethernet split run: gates, CU/DU logs, MCS/BLER/SNR, RLC/PDCP counters, F1-C/F1-U packet timing, CPU governors, and process/config identity.
2. Re-run controlled measurements if the lab is available:
   - Ethernet CU/DU split with the same phone, cage position, APN/DNN, speedtest method, and CPU governors.
   - Caged Quectel backhaul with the same phone position and test method.
   - Optional monolithic reference for RF ceiling.
3. For each run, record:
   - phone speedtest result and timestamp
   - access DU MCS/BLER/SNR lines during the test
   - CU/DU RLC/PDCP/GTP-U evidence
   - packet captures showing F1-C and F1-U placement
   - WireGuard stats for Quectel runs
   - CPU governor/load and any underrun/overflow logs
4. Test specific hypotheses:
   - Ethernet split was previously stuck in a low-MCS or bad feedback state.
   - The fresh TUI launch sequence cleared stale OAI/RRC/PDU session state.
   - Performance governors or process affinity improved timing.
   - The caged physical setup changed RF quality enough to dominate throughput.
   - WireGuard/Quectel path changed packet pacing, MTU, or jitter in a way that helped the access scheduler.
   - The previous 23 Mbps Ethernet result was measured under a different phone/APN/server/run condition.
5. Produce a short findings note with evidence, not speculation. Include the most likely root cause, confidence level, remaining unknowns, and the next experiment that would falsify the explanation.

Safety rules:
- Do not expose secrets, IMSIs, keys, raw packet captures, or unsanitized logs.
- Do not claim a throughput cause without evidence from logs, packet captures, or repeated controlled tests.
- Preserve the Ethernet CU/DU baseline as rollback.
