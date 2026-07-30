# Reproducibility guide

## Reproducibility status

This repository publishes the research record, static figures, and project
recap. Full deployment, the exact OAI revision and public patch set, baseline
definitions, validation gates, and rollback workflow are maintained in
[`promaaa/oai-cu-du-lab`](https://github.com/promaaa/oai-cu-du-lab). Private
runtime configuration and raw measurement bundles remain outside both
repositories.

That boundary is intentional and should be stated in any paper or public demo.

## Documentation artifacts

The Markdown reports and static figures require no installation. Open
[`visual-project-recap/index.html`](../visual-project-recap/index.html) directly
or serve that directory with any static file server to view the interactive
recap.

## Minimum experiment record

Every new run intended to support a comparative claim should record:

| Category | Required fields |
| --- | --- |
| Software | OAI repository URL, commit SHA, local patches, build flags |
| Topology | CU, DU, core, radio, UE, donor/backhaul path |
| Radio | SDR model, bandwidth/PRBs, band/ARFCN, gains, clock source |
| Transport | Interface, MTU, tunnel type, route policy, RTT, jitter, loss |
| Host | CPU, memory, kernel, governor, affinity, USB or Ethernet link speed |
| Test | Direction, tool, duration, warm-up, number of repetitions |
| Outcome | Throughput distribution, BLER, MCS, CPU, errors, packet-path proof |

## Comparison protocol

For a defensible transport comparison:

1. Freeze the OAI commit, radio profile, UE, RF placement, and core topology.
2. Change only the F1 transport under test.
3. Validate packet placement before accepting a result.
4. Run a warm-up followed by at least 10 equal-duration repetitions.
5. Collect synchronized CU, DU, core, tunnel, and host metrics.
6. Publish all samples or an anonymized machine-readable summary.
7. Report median, dispersion, sample count, and failures—not only the best run.

## Result labels used in this repository

- **Measured:** backed by a recorded run.
- **User-confirmed:** observed by the researcher but not yet accompanied by a
  complete public evidence bundle.
- **Calculated:** derived from documented inputs and formulas.
- **Planning estimate:** used for sizing or procurement and must be refreshed
  before a purchase or flight decision.

## Radio and PWS safety

Use shielding or authorized test spectrum and comply with local rules. Public
warning tests must remain isolated from live networks and must use explicit lab
identifiers and controlled UEs.
