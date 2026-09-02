# Research Gaps

## Incident-Level Evidence Gap

Indian public crime datasets are usually aggregated by State/UT, district, offence head, or year. Behavioural crime linkage requires incident-level fields: complaint narrative, modus operandi, event time, location, target type, property loss, victim-offender interaction, device identifiers, financial trails, and forensic handling metadata.

## Multilingual NLP Gap

Indian complaints frequently mix English, Hindi, regional-language vocabulary, transliteration, platform names, slang, and legal abbreviations. Generic English NLP models miss local intent and evidence cues. A useful paper contribution is a multilingual feature schema and evaluation protocol rather than an unsupported claim of universal language understanding.

## Digital-Forensic Quality Gap

Public funding or infrastructure data is not the same as forensic performance. The missing variables are acquisition method, hash verification, chain of custody, tool validation, examiner workload, lab turnaround time, backlog, and court acceptance.

## LLM Governance Gap

LLMs are useful for summarization, translation, evidence-gap prompting, and hypothesis generation. They must not make suspect-identification decisions, invent facts, or replace admissible forensic examination. The platform stores prompts and deterministic feature extraction so LLM output can be audited.

## Evaluation Gap

A credible paper should evaluate precision and recall against labeled incident-level cases or expert-coded synthetic cases. Aggregate NCRB or global crime statistics are not sufficient ground truth for behavioural linkage.
