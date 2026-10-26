# FactIndic Agent Manifest

Version: 1.0  
Project: CSET 346 — FactIndic  
Repository: `/home/ak/Code/FactIndic`

## Mission
Build a reproducible baseline for factuality-aware summarization across:
1. Hindi in Devanagari
2. English
3. Devanagari Hindi-English code-mixing
4. Roman-script Hinglish

Compare standard and factuality-aware prompts. Do not train or fine-tune models in this phase.

## Mandatory environment constraints
- OS: CachyOS Linux; shell: Fish.
- Python: pyenv-managed Python 3.12.8.
- **Never create, activate, or use any virtual environment.** No `venv`, `virtualenv`, Conda, Poetry env, Pipenv, or `pyenv-virtualenv`. Do not create `.venv`.
- Before installing packages, verify `python --version`, `sys.executable`, and `python -m pip --version`.
- If the interpreter is not pyenv Python 3.12.8, stop package installation and diagnose without changing global Python selection.
- Use `python -m pip` in the active pyenv interpreter; inspect versions first and avoid unnecessary upgrades.
- Do not use `sudo` for Python packages, alter system-wide configuration, install Ollama, delete user data, or overwrite working files blindly.
- Never reveal credentials or print `.env`.

## Provider and secrets
- Primary generation provider: Groq; last tested model `openai/gpt-oss-20b`.
- Environment variables: `GROQ_API_KEY`, `GROQ_MODEL`; load `.env` with `python-dotenv`.
- Keep `.env` out of Git. Never log credentials.
- Gemini is a future optional provider; previous requests returned 503/504. Do not block progress on it.
- Make provider/model configurable, log exact IDs and parameters, respect free-tier limits, and use bounded retries.

## Datasets
Inspect and validate before downloading large amounts:
- XL-Sum: https://huggingface.co/datasets/csebuetnlp/xlsum — Hindi and English configurations, schema, license, official splits, source/reference fields. Preserve official splits; avoid leakage.
- GupShup: https://anishacharya.github.io/papers/gupshup/ — verify access, license, scripts, splits, and paired summaries; do not bypass access restrictions.
- MUTANT: https://huggingface.co/datasets/LingoIITGN/MUTANT — verify schema/license and whether paired reference summaries exist.
- Roman Hinglish: verify actual coverage; if insufficient, create an annotation template. Do not fabricate collected data or label silent transliteration as naturally occurring Hinglish.

Keep raw and processed data separate (`data/raw`, `data/processed`, `data/manifests`). Preserve source, reference summary, title, split, category, and stable ID. Normalize only safe whitespace/formatting. Create JSON and CSV manifests with license, revision/config, split sizes, fields, category coverage, missing records, duplicates, status, and limitations. Do not commit large datasets/model weights.

## NER candidates: benchmark multiple
- `ai4bharat/IndicNER` — https://huggingface.co/ai4bharat/IndicNER
- `theanugrah/muril-indic-ner` — https://huggingface.co/theanugrah/muril-indic-ner
- `MichaelHuang/muril_base_cased_hindi_ner` — https://huggingface.co/MichaelHuang/muril_base_cased_hindi_ner
- `dslim/bert-base-NER` — https://huggingface.co/dslim/bert-base-NER (English baseline only)

Check access, license, language/script coverage, labels, model size, dependencies, and resource needs. Evaluate comparable candidates on the same manually annotated gold examples; report entity-level precision/recall/F1, category scores where sample sizes allow, latency, and memory. Select top two only if validation evidence supports it.

## NLI candidates: benchmark multiple
- `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` — https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli
- `joeddav/xlm-roberta-large-xnli` — https://huggingface.co/joeddav/xlm-roberta-large-xnli
- `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` — https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7

Create manually labelled source-evidence/summary-claim pairs: entailed/supported, contradicted, neutral/insufficient evidence. Map native model labels correctly. Report per-class precision/recall/F1, macro-F1, confusion matrix, latency, memory, and category results where sample size allows. NLI estimates evidence relation; it does not prove absolute truth.

## Evidence retrieval and deterministic checks
- Embedding candidate: `intfloat/multilingual-e5-small` — https://huggingface.co/intfloat/multilingual-e5-small
- Follow its model card, including `query:` and `passage:` prefixes.
- Retrieve source passages for summary claims; report Recall@k only when relevant evidence is annotated.
- Similarity alone is not factual support.
- Separately check dates, numbers, percentages, and currencies. Flag mismatches for review rather than automatically calling every mismatch false.

## Summarization and metrics
Use Groq for standard and factuality-aware prompting with matching generation settings. Record model ID, prompt version, latency, and errors.
Metrics where appropriate: ROUGE-1/2/L, multilingual BERTScore if justified, average summary length, defined compression ratio, mean/median latency, API failures, support/contradiction/neutral rates, and precision/recall/F1 only against human-labelled gold data. ROUGE/BERTScore are not factuality metrics.

## Pilot and scientific safeguards
- Begin with around 10–20 examples per accessible category if available and within free-tier limits; record actual counts.
- Preserve official splits and keep test data untouched during model/prompt selection.
- Cache/checkpoint completed API requests. Include dry-run and bounded pilot modes; full runs opt-in.
- Do not fine-tune during this phase. Never fabricate data or results.
- If annotations are insufficient, report the limitation and do not claim a definitive winner.

## Execution order
1. Inspect repository, Git status, pyenv Python 3.12.8.
2. Check `.env` safety and dependency versions.
3. Inspect dataset schema, license, access, and paired-summary coverage.
4. Download bounded pilot data and write manifests.
5. Inspect RAM/disk/CPU/GPU.
6. Install only needed compatible packages into active pyenv Python; never create a venv.
7. Load/test viable NER candidates.
8. Load/test viable NLI candidates.
9. Test E5 retrieval and numeric/date checks.
10. Create annotation templates/guidelines.
11. Benchmark candidates on comparable gold-labelled validation data.
12. Select top two NER and NLI only when justified.
13. Run Groq on both prompt conditions.
14. Run bounded pilot evaluation.
15. Test artifacts and write report.

## Portable session protocol
At every session start, read this file, `AGENT_LOG.md`, and `PROJECT_STATE.json`, then inspect actual repo state. At each meaningful work unit, append to the log and update valid JSON state.

### `AGENT_LOG.md`
Append timestamped entries; include phase, files changed, commands (no secrets), actual outcomes, errors/blockers, decisions, and next actions. Never rewrite history; append corrections.

### `PROJECT_STATE.json`
Update after each meaningful work unit. Keep valid JSON. Record last-updated ISO timestamp, environment verification, current phase, completed/in-progress/blocked tasks, dataset/model statuses, selected models or `null`, last checkpoint, next three actions, and artifact paths. Do not mark unverified work complete.

## Required deliverables
Dataset manifest/report; preparation scripts; NER/NLI annotation template and benchmarks; retrieval and number/date checks; configurable Groq generator and prompts; pilot predictions and metrics; tests; README reproduction instructions; this manifest, log, and state.

## Final report
Report only verified actions/results, exact model IDs and versions, dataset access/size/license/splits, language coverage, candidate comparison, tests, artifact paths, blockers, and next actions. Never expose secrets or claim unexecuted work.
