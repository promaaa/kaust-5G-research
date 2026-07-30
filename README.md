# Airborne OpenAirInterface 5G CU/DU Research Testbed

This repository documents an experimental OpenAirInterface (OAI) 5G standalone
testbed built to study a disaggregated gNB, heterogeneous F1 transport, public
warning delivery, and embedded distributed-unit candidates for an eventual
airborne deployment.

The central research question is practical: **how do compute constraints, radio
conditions, and non-ideal F1 transport interact in an OAI CU/DU split?**

> This is a research record, not a production network distribution. It contains
> reports, diagrams, measurements, and chart-generation utilities. The
> deployment automation, public patch set, baseline definitions, and rollback
> workflow are maintained in
> [`promaaa/oai-cu-du-lab`](https://github.com/promaaa/oai-cu-du-lab), which is
> the canonical operational source.

![Best-observed throughput across shared configurations](docs/Presentation/img/throughput_chart_best.png)

## Current findings

The work progressed from a monolithic OAI baseline to Ethernet, Wi-Fi/GRE, and
5G-modem/WireGuard F1 paths; it also validated PWS/SIB8 delivery and several
embedded DU candidates.

| Configuration | Best result recorded | Evidence |
| --- | ---: | --- |
| Monolithic x86 reference | 190 Mbps | [Report 19](docs/Presentation/Research%20Progress%20Report%2019.md) |
| Tuned Ethernet CU/DU split | 100 Mbps peak | [Report 19](docs/Presentation/Research%20Progress%20Report%2019.md) |
| Wi-Fi/GRE CU/DU split | 52 Mbps | [Report 19](docs/Presentation/Research%20Progress%20Report%2019.md) |
| Quectel/WireGuard CU/DU split | 78 Mbps | Latest researcher-confirmed run; encoded in the [chart source](scripts/generate_throughput_charts.py) |
| Jetson + Quectel/WireGuard | about 40–44 Mbps | [Reports 21–22](docs/Presentation/README.md#late-stage-results) |

These values are best-observed results from different hosts and test sessions.
They are **not** controlled statistical averages and should not be interpreted
as a platform benchmark. Reports 18–22 document the later MTU/MSS, BLER,
scheduler, USB, and host-tuning findings that supersede earlier working
hypotheses.

## Repository map

| Path | Purpose |
| --- | --- |
| [`docs/`](docs/README.md) | Documentation index and reading order |
| [`docs/Notes/`](docs/Notes/) | Setup notes, procedures, and project synthesis |
| [`docs/Presentation/`](docs/Presentation/README.md) | Chronological progress reports and presentation sources |
| [`docs/Other/`](docs/Other/README.md) | Technical scratch notes and annotated implementation images |
| [`docs/References/`](docs/References/README.md) | Literature list with links to original sources |
| [`docs/analysis/`](docs/analysis/) | Working assessment of scientific positioning |
| [`visual-project-recap/`](visual-project-recap/) | Self-contained HTML/Markdown/PDF project recap |
| [`scripts/`](scripts/) | Repository checks and reproducible chart generation |

## Quick start

Run the repository checks with the Python standard library:

```bash
python3 scripts/check_repository.py
```

Regenerate the throughput charts in an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/generate_throughput_charts.py
```

View the self-contained recap locally:

```bash
python3 -m http.server --directory visual-project-recap 8000
```

Then open `http://localhost:8000`.

The `docs/` directory can also be opened as an Obsidian vault. Install
**Advanced Slides** from Obsidian's community-plugin browser if you want to
render the slide-oriented Markdown files; the plugin itself is intentionally
not vendored.

## Reproducibility and responsible use

Start with [the reproducibility guide](docs/REPRODUCIBILITY.md). It distinguishes
reported observations from repeatable artifacts and defines the minimum
evidence expected for future measurements.

This work uses software-defined radio equipment. Operate only with suitable
shielding or authorization, approved frequencies and power levels, and local
regulatory and institutional permission. Never test public-warning behavior on
a live public network.

## Contributing, security, and licensing

See [CONTRIBUTING.md](CONTRIBUTING.md) before adding reports or measurements and
[SECURITY.md](SECURITY.md) before reporting a vulnerability or handling lab
credentials.

No public-use license has been selected yet. Until the copyright holder confirms
one, normal copyright restrictions apply. License selection and author/citation
metadata remain explicit items in the
[publication checklist](docs/PUBLICATION_CHECKLIST.md).
