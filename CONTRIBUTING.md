# Contributing

Contributions that improve reproducibility, correct technical errors, or add
well-scoped experimental evidence are welcome.

## Before opening a change

1. Keep one research claim per report section and distinguish observations,
   interpretations, and hypotheses.
2. Record the OAI commit, host, radio, bandwidth/PRB profile, transport path,
   configuration changes, and measurement method.
3. Report repeated measurements when making comparative performance claims.
   Include sample count and a summary statistic; do not present a single
   best-observed run as an average.
4. Link to third-party papers instead of committing publisher PDFs.
5. Remove credentials, subscriber identifiers, hardware serial numbers, public
   IP addresses, personal data, and machine-specific home-directory paths.
6. Confirm that photographs and screenshots are safe and licensed for public
   distribution.

## Local checks

```bash
python3 scripts/check_repository.py
```

If a change affects chart inputs, regenerate the outputs:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/generate_throughput_charts.py
```

Review all generated images visually before committing them.

## Writing conventions

- Use sentence-case headings.
- Spell out an acronym on first use.
- Use `Mbps` for megabits per second and `MB/s` only for megabytes per second.
- Prefer relative links so files render on GitHub and in local clones.
- Give images descriptive alt text.
- Preserve historical reports, but add a dated correction when later evidence
  supersedes an earlier conclusion.

## Security

Do not open a public issue containing a credential or vulnerability. Follow
[SECURITY.md](SECURITY.md).

