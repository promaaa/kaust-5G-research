# Airborne OpenAirInterface 5G CU/DU Research Testbed

This repository documents an experimental OpenAirInterface (OAI) 5G standalone
testbed built to study a disaggregated gNB, heterogeneous F1 transport, public
warning delivery, and embedded distributed-unit candidates for an eventual
airborne deployment.

The central research question is practical: **how do compute constraints, radio
conditions, and non-ideal F1 transport interact in an OAI CU/DU split?**

> This is a research record, not a production network distribution. It contains
> reports, diagrams, measurements, and a project recap. The
> deployment automation, public patch set, baseline definitions, and rollback
> workflow are maintained in
> [`promaaa/oai-cu-du-lab`](https://github.com/promaaa/oai-cu-du-lab), which is
> the canonical operational source.

![Best-observed throughput across shared configurations](reports/assets/best-throughput.png)

## Current findings

The work progressed from a monolithic OAI baseline to Ethernet, Wi-Fi/GRE, and
5G-modem/WireGuard F1 paths; it also validated PWS/SIB8 delivery and several
embedded DU candidates.

| Configuration | Best result recorded | Evidence |
| --- | ---: | --- |
| Monolithic x86 reference | 190 Mbps | [Report 19](reports/report-19.md) |
| Tuned Ethernet CU/DU split | 100 Mbps peak | [Report 19](reports/report-19.md) |
| Wi-Fi/GRE CU/DU split | 52 Mbps | [Report 19](reports/report-19.md) |
| Quectel/WireGuard CU/DU split | 78 Mbps | Latest researcher-confirmed run; summarized in the [project recap](visual-project-recap/presentation.md) |
| Jetson + Quectel/WireGuard | about 40–44 Mbps | [Reports 21–22](reports/README.md#late-stage-results) |

These values are best-observed results from different hosts and test sessions.
They are **not** controlled statistical averages and should not be interpreted
as a platform benchmark. Reports 18–22 document the later MTU/MSS, BLER,
scheduler, USB, and host-tuning findings that supersede earlier working
hypotheses.

## Repository map

| Path | Purpose |
| --- | --- |
| [`reports/`](reports/README.md) | Chronological reports, one French presentation, and supporting assets |
| [`technical-notes/`](technical-notes/README.md) | Terminology, F1 configuration notes, and informal reading notes |
| [`REFERENCES.md`](REFERENCES.md) | Curated literature list with original-source links |
| [`visual-project-recap/`](visual-project-recap/) | Self-contained HTML/Markdown/PDF project recap |

## View the project recap

View the self-contained recap locally:

```bash
python3 -m http.server --directory visual-project-recap 8000
```

Then open `http://localhost:8000`.

Related Google Slides presentations used for this project:

- [Présentation Charlotte V2](https://docs.google.com/presentation/d/1PTyXXZYdgLUkJzEHDRDvrb-UP5atUvs2Kw81VID5y84/edit?slide=id.g3ec4f7470cd_0_76#slide=id.g3ec4f7470cd_0_76)
- [Présentation stage](https://docs.google.com/presentation/d/1-PejsoKiz7iE7Y6ZO_rdnELiBxwlDJI5kkbP2ylJjug/edit?slide=id.g3ec4f7470cd_0_76#slide=id.g3ec4f7470cd_0_76)

The repository root can also be opened as an Obsidian vault. Install Advanced
Slides separately if you want to render the French slide-oriented Markdown
source; no editor plugin code or local settings are stored here.

## Responsible use

This work uses software-defined radio equipment. Operate only with suitable
shielding or authorization, approved frequencies and power levels, and local
regulatory and institutional permission. Never test public-warning behavior on
a live public network.

## Licensing

No public-use license has been selected yet. Until the copyright holder confirms
one, normal copyright restrictions apply.
