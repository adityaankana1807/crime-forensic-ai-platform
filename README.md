# AI-Driven Multilingual Crime Behaviour and Digital-Forensic Evidence Analysis Platform

Research prototype for crime-behaviour analytics, multilingual NLP triage, and digital-forensic evidence-gap analysis with India-focused and global public datasets.

## Run Locally

```powershell
python scripts/build_datasets.py
python -m unittest discover -s tests
python -m app.server
```

Open `http://127.0.0.1:8000`.

## What Is Implemented

- Complete static frontend in `public/`.
- Python backend API in `app/server.py`.
- Deterministic NLP/evidence triage in `app/analysis.py`.
- India cybercrime and cyber-forensic capacity datasets from PIB/NCRB-derived public tables.
- Global comparison datasets from World Bank/UNODC, UK Police API, and DOJ/BJS NIBRS estimates API.
- Dataset manifest with provenance, granularity, row counts, and limitations.
- Paper-oriented research gap documentation.

## What This Does Not Claim

This is not an operational police system. It does not identify suspects, process private evidence, or prove forensic admissibility. Public aggregate datasets are valid for trend comparison, not incident-level behavioural linkage.

## Project Structure

```text
app/                  backend and NLP logic
data/processed/       generated CSV and JSON datasets
docs/                 paper methodology notes
public/               frontend assets and public data JSON
scripts/              dataset builder
tests/                unit tests
```
