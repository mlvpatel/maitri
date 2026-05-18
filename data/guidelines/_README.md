# Guideline Corpus (placeholder)

For the hackathon MVP we ingest ~200 chunks (~800 tokens each) from:

- WHO Antenatal Care Recommendations (2016 + 2025 update) — public, CC-BY
- WHO Recommendations for Prevention and Treatment of Pre-eclampsia and Eclampsia — public
- FIGO 2024 Hypertensive Disorders in Pregnancy — public guideline excerpts
- India ICMR + RMNCH+A maternal-health protocols — public, GoI

**No PDFs are committed to the repo** — the loader script ingests from versioned source URLs (in `src/rag/ingest.py`) and writes the LanceDB index to a local file. This keeps the repo light and license-clean.

The chunk corpus *metadata* (titles, source URLs, retrieval keys, last-reviewed-by-clinician timestamp per chunk) lives in `corpus_metadata.csv` (created at first run).

Each chunk is tagged with:
- `source_id`, `source_url`, `version`, `published_date`
- `country_scope` (`global` or ISO-3166)
- `language` (`en` for hackathon)
- `topic` (e.g. `hypertensive_disorders`, `gestational_diabetes`, `anemia`, `infection_screening`)
- `chunk_id`, `chunk_text`, `embedding`

The Retrieval Agent enforces filter `country_scope ∈ {global, IND}` for the demo.
