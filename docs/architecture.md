# Architecture

## Frontend

The static frontend in `public/` renders dataset provenance, India cybercrime growth, research gaps, and NLP triage results. It calls the backend APIs with `fetch`.

## Backend

`app/server.py` serves static files and exposes:

- `GET /api/health`
- `GET /api/datasets`
- `GET /api/dashboard`
- `GET /api/india/cybercrime`
- `GET /api/gaps`
- `POST /api/analyze`

`app/analysis.py` performs deterministic NLP extraction for crime categories, Indian language hints, digital indicators, evidence coverage, risk scoring, and LLM-review prompt generation.

## Data Pipeline

`scripts/build_datasets.py` writes compact CSVs under `data/processed/` and public JSON manifests under `public/data/`. API-fetched datasets should be regenerated before final paper submission because live public datasets can change.

## LLM Integration Point

The prototype does not call an external LLM by default. The `/api/analyze` response includes an `llm_review_prompt` that can be sent to a configured LLM after institutional review, data minimization, and privacy controls are in place.
