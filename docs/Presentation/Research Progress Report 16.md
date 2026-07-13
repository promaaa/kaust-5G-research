# State of the art and added value

**Date:** June 19, 2026
**Timeline:** April 7 to July 31, 2025 (16 weeks)

---

## What changed since last update

1. Two deep-research reports synthesized into a sharper positioning of the project against the literature.
2. The six research areas mapped in Report 15 were re-graded against the closest existing works.
3. Each project element was scored individually for novelty and for the evidence gap that still blocks publication.
4. The five candidate publication angles were re-evaluated and the recommended merge was made explicit.
5. The strongest single defensible claim was restated in one sentence, with everything else tagged as preliminary.

---

## Purpose of this report

Report 15 placed the project against the literature at a high level. This report goes deeper using both deep-research documents as a structured lens, and answers a sharper question:

> Which of our project elements are already covered by the state of the art, which are genuinely different, and what is the single most defensible claim we can make today?

The two deep-research reports agree on a shared conclusion. Our setup is a strong engineering and integration artifact, but several elements we initially treated as novel are already documented elsewhere. The combination is what remains distinctive, and the strongest scientific claim sits in the F1 heterogeneous transport study and the MCS collapse observed during split runs.

---

## State of the art, in six areas

The literature reviewed in the deep-research reports falls into six areas. In every area, the underlying primitive already exists; our contribution sits in the coupling and in the experimental discipline.

- **OAI and open-source 5G platforms.** OAI RAN, OAI 5GC, O-RAN 7.2x split, F1, E1, and CI-CD pipelines are widely documented. Running OAI alone is not novel. Our TUI and reproducibility pipeline are the lab differentiator.
- **CU/DU split and F1.** 3GPP Option 2 with F1-C on SCTP and F1-U on GTP-U over UDP 2153 is standardized, and OAI supports it natively. The split itself is not novel. Treating F1 transport as the experimental variable is the lab differentiator.
- **Wireless or non-ideal midhaul.** IAB, aerial DU on OAI, NTN and satellite midhaul, and generic IP encapsulation have been studied. Our specific combination of Wi-Fi GRE plus commercial 5G plus WireGuard is rarely documented end-to-end on one platform.
- **PWS and SIB8.** The 3GPP PWS procedure via SIB8 and the F1AP Write-Replace Warning are standardized, and recent OAI work implements alert generation and spoofing studies. Tying PWS to a real CU/DU split with transport variation is the lab differentiator.
- **Lightweight or edge 5G.** srsRAN on Raspberry Pi 5 has been demonstrated by the Pi5G project. Running an OAI DU on Pi 5 with heterogeneous F1 is not yet profiled.
- **Reproducibility and testbed methodology.** NIST O-RAN automation, public scripts, and datasets are valued. Our TUI combines preflight, packet placement validation, and rollback in one operator script.

The right reading is that every area contains both "already done" and "our contribution". The contribution is almost always the coupling, not the primitive.

---

## Closest existing works

```yaml
closest_works:
  - "Aerial DU with OAI, 2023: https://arxiv.org/html/2305.05983v3"
  - "UL-TDoA in OAI, 2024: https://www.researchgate.net/publication/395633861"
  - "On-demand 5G private networks using a mobile cell, 2024: https://arxiv.org/pdf/2411.06597"
  - "Lisi et al., transparent 5G NTN over Starlink, 2024: https://www.mdpi.com/2673-8732/5/3/25"
  - "NIST O-RAN testbed automation, 2024: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=960654"
  - "Experimental comparison of srsRAN and OAI on SDR, 2024: https://arxiv.org/html/2406.01485v1"
  - "Performance analysis of full-fledged 5G SA TDD testbeds, 2024: https://arxiv.org/html/2407.02341v1"
  - "Pi5G, lightweight 5G testbed on Raspberry Pi 5, 2024/2025: https://www.researchgate.net/publication/404659481"
  - "Modular design and experimental evaluation of 5G mobile cell architectures, 2025: https://www.researchgate.net/publication/394397570"
  - "dApps performance characterization in O-RAN, 2026: https://arxiv.org/html/2605.05426v1"
  - "Elango et al., CPU-GPU frequency interactions in GPU-accelerated 5G O-RAN, 2024: https://ece.northeastern.edu/fac-ece/dkoutsonikolas/publications/ngopera26.pdf"
  - "From Spoofing to Trust, emergency alerts testbed on OAI, 2026: https://arxiv.org/abs/2604.24404"
```

No single work covers the full quartet of OAI CU/DU split, heterogeneous F1 transport, PWS over split, and Pi 5 DU. Several works cover pairs. The remaining novelty is the quartet plus the TUI plus packet placement validation.

---

## What is already covered by others

These items are not novel by themselves, and the next paper draft should not present them as such.

```yaml
already_known:
  - "OAI can be used to run 5G SA testbeds"
  - "CU/DU split over F1 exists and is supported in OAI"
  - "F1-C uses SCTP and F1-U uses GTP-U over UDP"
  - "Remote and wireless DU scenarios have been explored, including aerial DU"
  - "Public warning systems and SIB8 have been studied, including on OAI"
  - "Raspberry Pi 5 can host a 5G testbed, demonstrated with srsRAN"
  - "Automation and reproducibility are first-class concerns in open RAN experimentation"
  - "IAB and 3GPP-style wireless backhaul are standardized"
```

The fact that these elements are not novel does not weaken the project. It clarifies the level of claim that is appropriate.

---

## What we bring, re-evaluated element by element

The deep-research reports graded each project element on originality, evidence gap, and path to publishable. We reproduce the assessment applied to our current evidence.

The publishable core sits in five items: the bottleneck and MCS collapse analysis (medium to high originality, strong evidence after the BLER window finding), the F1 over Wi-Fi GRE comparison, the F1 over Quectel 5G plus WireGuard comparison, the packet placement validation as a methodological backbone, and the PWS and SIB8 path in a real CU/DU split with UE-visible delivery.

The credibility and artifact support sits in six items: the multi-machine OAI CU/DU split itself, the monolithic versus split baseline, the radio and scheduler metric collection (MCS, NPRB, BLER, SNR, scheduler, F1, UPF/SMF), the Ethernet F1 baseline, the access and backhaul separation with packet evidence, and the TUI plus rollback plus LaTeX handoff.

The Pi 5 as a fully profiled OAI DU is partial: the cutover is done but the sustained CPU, RAM, and thermal profile is not yet measured.

The portable or drone-carried DU use case stays as future work: the architecture exists but no field test has been done.

The MCS pinned at 0 observation is no longer a stand-alone finding. It is now subsumed into the bottleneck claim, since the BLER window default in `MACRLC_nr_paramdef.h` was identified as the cause and a concrete mitigation was applied.

---

## Five candidate publication angles, graded

The deep-research documents proposed five angles. We restate them with current evidence.

- **A. Reproducible OAI CU/DU testbed.** Novelty is medium. Evidence needed is a clean repo, a frozen commit, and a hardware manifest. Venue fit is strong for WiNTECH, INFOCOM CNERT, and NetSoft. Probability is high.
- **B. F1 heterogeneous transport characterization.** Novelty is medium to high. Evidence needed is a fixed commit, fixed radio, ten or more runs per scenario, and synchronized traces. Venue fit is strong for VTC, EuCNC, and ICC or GLOBECOM workshops. Probability is medium to high.
- **C. PWS and SIB8 over CU/DU split.** Novelty is medium to high in a niche. Evidence needed is a 3GPP normative map and per-UE validation. Venue fit is best for demo tracks and workshops. Probability is medium.
- **D. Portable or edge DU with wireless backhaul.** Novelty is low to medium today. Evidence needed is a sustained run with CPU, RAM, and thermal profile. Venue fit is best for demo or poster, and a Pi5G comparison is required. Probability is low to medium.
- **E. Root-cause analysis of OAI CU/DU bottleneck.** Novelty is medium to high. Evidence is now in place after the BLER window finding. Venue fit is strongest for a workshop or short paper. Probability is medium to high.

The cleanest submission today merges A and B, with C as a use case and E as the central scientific story. Angle D is not yet mature enough to anchor a paper.

---

## Where our project actually adds value

Four contributions are genuinely additive.

```yaml
added_value:
  f1_transport_comparison:
    what: "Ethernet, Wi-Fi GRE, and Quectel WireGuard measured under a shared protocol"
    why_defensible: "TUI gates and packet placement validation prove the path under test"

  mcs_collapse_analysis:
    what: "MCS collapse in older Ethernet split runs, recovered through a concrete OAI scheduler parameter change"
    why_defensible: "The change is small, documented in OAI source, and reproducible"

  pws_over_split:
    what: "F1AP Write-Replace Warning implemented in OAI and validated on a Nothing Phone"
    why_defensible: "The path matches the 3GPP normative procedure"

  reproducible_testbed:
    what: "TUI gates, preflight, rollback, and packet placement validation in one operator script"
    why_defensible: "The TUI runs clean-room from cold install and produces artifacts"
```

The strongest single sentence we can defend today is:

> We built a reproducible OAI CU/DU split platform, characterized three heterogeneous F1 transport paths, identified and resolved an MCS collapse caused by the default scheduler BLER window, and validated a PWS warning path end-to-end on a commercial handset.

That sentence is conservative, accurate, and aligned with both deep-research documents.

---

## What is not yet a contribution

Three directions should be presented as preliminary, not as contributions.

- **Single-B210 RF backhaul end-to-end.** PRACH detection on the donor is not yet passing. A device-layer integration must reach PRACH, then registration, then F1 over RF.
- **Pi 5 as a fully profiled OAI DU.** Cutover is done, but sustained CPU, RAM, and thermal profile under several scenarios is not yet measured.
- **Drone-carried or portable DU use case.** Concept exists, no field test. A defended emulation or a field demonstration is required.

These should be carried as next-step or future-work items, not as headline claims.

---

## Mapping our performance numbers to the state of the art

The numbers collected across Reports 7 to 14 read very differently once the state of the art is fixed in mind. Monolithic at 150 to 190 Mbps with MCS 18 to 23 is consistent with OAI monolithic baselines in the literature. The older Ethernet split ceiling of 19 to 23 Mbps with MCS pinned at 0 sat well below expectation and was correlated with the BLER window default of 0.05. After the BLER target relax, Ethernet split reached 89 Mbps phone-side with MCS 24 to 27 dominant, aligning with the WireGuard split result and confirming the radio was never the bottleneck. The Wi-Fi GRE split at about 12 Mbps needs clean repetition. The Quectel WireGuard split at 42 to 50 Mbps with MCS up to 27 is a distinctive combination in the literature and validates the architecture once path validation is in place.

The single most useful insight from this mapping is that the older Ethernet split ceiling of 22 Mbps was an OAI scheduler artifact, not a transport limit. The radio was always capable of more.

---

## Risks, restated briefly

The deep-research documents list risks that an aggressive reviewer would raise. The largest open blocker is the repetition campaign under a frozen commit and fixed radio. Without it, the performance numbers stay at the level of observations, not evidence. Radio noise confounded with transport is partially mitigated by Faraday cage work but not fully closed. The monolithic-versus-split, "integration report" perception is mitigated by framing the introduction and discussion around F1 transport pathology rather than around installation steps. PWS judged out of scope is mitigated by presenting PWS as a use case for the split testbed.

---

## Suggested framing for the professor meeting

If asked to summarize the project in one paragraph, the following version aligns with both deep-research documents.

```yaml
framing:
  state_of_the_art: "OAI testbeds, CU/DU split, wireless backhaul, PWS over OAI, and lightweight 5G all exist separately in the literature"
  our_position: "We combine them into one reproducible OAI platform with packet placement validation and a TUI that enforces operator discipline"
  strongest_claim: "F1 transport heterogeneity, measured under a fixed protocol, has visible and reproducible effects on the scheduler; the older Ethernet split ceiling of 22 Mbps was a default-configuration artifact, lifted by relaxing the BLER target window"
  bonus_claim: "PWS over a real CU/DU split reaches a commercial handset, validating the split warning path"
  next_step: "Run the controlled campaign with frozen commit and fixed radio, then publish a workshop paper or artifact paper"
```

---

## What this report changes versus Report 15

| Before (Report 15) | After (Report 16, this report) |
| --- | --- |
| Each project element treated as a candidate contribution | Each element graded against the state of the art and ranked |
| Numbers presented as observations | Numbers mapped to state-of-the-art baselines and to the BLER window finding |
| Five angles listed with rough novelty | Five angles graded with venue fit, probability, and the recommended merge |
| Future work listed in one line | Three preliminary directions explicitly separated from contributions |

This is the version of the positioning that should anchor the discussion with the professor.

---

## Next steps

1. Lock the project framing on the merge of angles A, B, and E, with C as a use case, and update the LaTeX draft to match this report.
2. Run the controlled repetition campaign (frozen commit, fixed radio, 10 to 20 runs per scenario) on monolithic, Ethernet split, Wi-Fi GRE split, and Quectel WireGuard split.
3. Add the BLER target relax to the TUI so the 89 Mbps Ethernet result survives the next operator workflow.
4. Surface the B210 single-owner constraint, the BLER window finding, and the packet placement gates in the lab wiki so future operators start from the current evidence.
5. Continue the single-B210 RF backhaul work from the device-layer integration, with PRACH detection as the next radio gate.
6. Decide venue with the professor after the repetition campaign: WiNTECH, INFOCOM CNERT, VTC, EuCNC, or NetSoft as primary candidates, with a demo track as fallback for the PWS path.