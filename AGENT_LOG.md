# FactIndic Agent Activity Log

Append-only log for Copilot Agent and other assistants.

Rules:
- Append a timestamped entry after each meaningful work unit.
- Never rewrite or delete historical entries; append corrections.
- Never include API keys, `.env` contents, or other secrets.
- Record actual outcomes, not assumptions.
- Read this log and `PROJECT_STATE.json` at session start; update both at session end.

---

## Initial setup
- Status: portable starter files prepared.
- Manifest: `AGENT_MANIFEST.md`
- State: `PROJECT_STATE.json`
- Next: ask Copilot Agent to read the manifest and resume from the checkpoint.
- This entry records starter-file creation only; dataset/model tasks have not yet been executed.

## 2026-10-26T11:35:05+05:30 — Repository and interpreter inspection
- Phase: repository inspection.
- Files inspected: `AGENT_MANIFEST.md`, `AGENT_LOG.md`, `PROJECT_STATE.json`, `.gitignore`, `check_gemini.py`, `test_groq.py`.
- Commands run: `git status` (workspace is not a Git repository); `python --version`; `python -c` for `sys.executable`; `python -m pip --version`; `pyenv version`; `pyenv versions`; dependency presence probe; workspace size/directory inspection.
- Outcome: `.env` is present and listed in `.gitignore`; no credentials were read or logged. Workspace contains only starter files and `__pycache__`; no dataset or project Git metadata is present.
- Environment outcome: default pyenv selection is `system`, yielding Python 3.14.8 at `/usr/bin/python`; required pyenv Python 3.12.8 is installed and verified at `/home/ak/.pyenv/versions/3.12.8/bin/python` using per-command `PYENV_VERSION=3.12.8`, without changing global selection or creating a virtual environment.
- Dependency outcome under Python 3.12.8: `python-dotenv`, `groq`, `datasets`, `transformers`, and `torch` are installed; `sentence_transformers` and `rouge_score` are not installed.
- Errors/blockers: repository is not initialized as Git; default interpreter does not meet the manifest requirement. Package installation is deferred until the required interpreter is active for commands.
- Decision: continue all project commands with `PYENV_VERSION=3.12.8`; do not install packages or alter global pyenv selection yet.
- Next actions: inspect dataset schemas/licenses/access and paired-summary coverage; then download a bounded pilot and create manifests.

## 2026-10-26T11:41:00+05:30 — Dataset access and schema inspection
- Phase: dataset inspection.
- Commands run: Hugging Face dataset metadata/tree/card requests for XL-Sum and MUTANT; GupShup landing page and official GitHub README/API requests; XL-Sum loader inspection; hosted first-row service probes; resource checks.
- XL-Sum outcome: public, ungated dataset revision `30fece425f9a3866e04321773ca7a80056d55ca6`; license CC BY-NC-SA 4.0; Hindi and English configs expose `id`, `url`, `title`, `summary`, and `text`, with train/validation/test splits. Official card counts are Hindi 70,778/8,847/8,847 (88,472 total) and English 306,522/11,535/11,535 (329,592 total). Source archives are 82,265,197 bytes (Hindi) and 282,122,304 bytes (English). The hosted first-row/parquet services returned 404/500 for this legacy script dataset, so bounded examples require archive extraction.
- MUTANT outcome: public, ungated revision `e7a454a71d4f9d1f3ebb65544868610e513d9366`; license CC BY 4.0; card describes Hindi-English code-mixed texts, 67,007 documents and 84,937 multi-sentential code-mixed texts. Hosted first-row service returned text-only rows for config `Aap`; the repository uses source `.txt` files and configs such as Aap, Bhaskar, INC, Jagran, Mankibaat, PM-speech, and PIB. No paired reference-summary field or standard held-out split was found in the inspected metadata.
- GupShup outcome: official page and repository are accessible, but the repository instructs users to request data through a Google Form. It documents h2e and e2e tasks with `.source` and `.target` train/test files; no data was downloaded or access bypass attempted. GitHub repository license is MIT; this does not establish a separate dataset license.
- Errors/blockers: XL-Sum’s legacy `xlsum.py` cannot be loaded by the installed `datasets` version (“Dataset scripts are no longer supported”); MUTANT builder inspection also failed due current `trust_remote_code` handling, but hosted rows and card/tree metadata were available.
- Decision: use official XL-Sum archive extraction for a bounded pilot; include MUTANT text-only samples as a non-reference corpus; mark GupShup blocked pending authorized access; do not claim paired summaries for MUTANT or GupShup.
- Next actions: download only the two XL-Sum source archives needed to extract bounded pilot examples, collect bounded MUTANT rows, and write raw/processed manifests with limitations.

## 2026-10-26T11:41:38+05:30 — Bounded pilot and manifests
- Phase: bounded pilot data preparation.
- Files added: `scripts/prepare_pilot.py`, `data/raw/xlsum/hindi_XLSum_v2.0.tar.bz2`, `data/raw/xlsum/english_XLSum_v2.0.tar.bz2`, `data/raw/mutant/aap_first_rows.json`, processed JSONL pilots, and JSON/CSV manifests under `data/manifests`.
- Commands run: downloaded the official XL-Sum Hindi and English archives; checked archive members and SHA-256; compiled and ran `scripts/prepare_pilot.py --limit-per-split 20`; fetched the public MUTANT Aap first-row endpoint; validated JSON and record counts.
- XL-Sum outcome: 60 Hindi records and 60 English records prepared, exactly 20 each from train, validation, and test. Required source, reference summary, title, split, category, stable ID, and source URL fields are present; duplicate/empty checks passed. Archive hashes: Hindi `23e625cfdd596ae59bab6e1756756c4d68bf50f355437943b3e57f0593662193`; English `ce2e965b9e4b8b337a801fda8b55e673fe2b17c4f3755d7fff886944633fec29`.
- MUTANT outcome: 32 hosted rows returned, 16 non-empty texts written to the pilot. Empty separator rows were excluded. Records contain source text and stable IDs only; `reference_summary` is explicitly null.
- Errors/corrections: initial MUTANT conversion expected 20 non-empty rows but the endpoint returned only 16; the conversion was corrected to preserve all 16 actual records. No fabricated rows were added.
- Validation outcome: `PROJECT_STATE.json`, both dataset manifests, and pilot JSONL structure validated; total processed pilot count is 136 records.
- Next actions: inspect runtime/package compatibility, install only missing packages under verified Python 3.12.8 if needed, then create annotation templates and model evaluation preparation.

## 2026-10-26T11:45:00+05:30 — Dependency preparation
- Phase: dependency preparation.
- Commands run: inspected package versions; reconfirmed Python 3.12.8, executable, and pip; installed `sentence-transformers` and `rouge-score` with `PYENV_VERSION=3.12.8`; imported both packages; ran `python -m pip check`.
- Outcome: installed `sentence-transformers 6.2.0` and `rouge-score 0.1.2`; imports succeeded and pip reported `No broken requirements found`.
- Existing versions inspected: `python-dotenv 1.2.4`, `groq 1.7.0`, `datasets 5.1.0`, `transformers 5.20.2`, and `torch 2.14.1`.
- Constraints respected: no virtual environment was created or used; no global pyenv selection was changed; no secrets were read or logged.
- Next actions: create NER/NLI annotation templates and guidelines, then inspect viable candidate model metadata and resource requirements.

## 2026-10-26T11:48:00+05:30 — Candidate model metadata inspection
- Phase: model metadata inspection.
- Commands run: Hugging Face model API requests for all listed NER candidates, all listed NLI candidates, and `intfloat/multilingual-e5-small`; extracted revisions, access flags, licenses, pipeline tags, languages, and architectures.
- NER outcome: `ai4bharat/IndicNER` is multilingual Indic token classification, MIT, gated-auto; `theanugrah/muril-indic-ner` is multilingual Indic ONNX NER, Apache-2.0, ungated; `MichaelHuang/muril_base_cased_hindi_ner` is Hindi NER, ungated; `dslim/bert-base-NER` is English-only, MIT, ungated.
- NLI outcome: all three candidates are multilingual zero-shot/NLI models with Hindi coverage in metadata and MIT licenses; revisions were recorded from the API. No model was selected.
- Retrieval outcome: `intfloat/multilingual-e5-small` is public, MIT, sentence-similarity, multilingual including Hindi and English; revision `614241f622f53c4eeff9890bdc4f31cfecc418b3`.
- Decision: metadata is evidence for access/coverage only; selection requires smoke tests and comparable manually labelled validation data. No benchmark or winner claim was made.
- Next actions: smoke-test accessible NER/NLI candidates and E5 with bounded inputs, then record resource/latency observations.

## 2026-10-26T11:55:00+05:30 — Model smoke tests
- Phase: model smoke testing.
- Command run: one CPU-only Python process loaded `MichaelHuang/muril_base_cased_hindi_ner`, `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli`, and `intfloat/multilingual-e5-small`, ran bounded inputs, and recorded latency/resource observations.
- NER outcome: model loaded and produced `LABEL_22` output in 64.736 seconds; config has 23 generic labels (`LABEL_0`–`LABEL_22`), so semantic category mapping is unresolved and no NER score was computed.
- NLI outcome: model loaded in 58.725 seconds; native mapping is entailment/neutral/contradiction. Example pair scores were entailment 0.9916893244, neutral 0.0060555455, contradiction 0.0022550842.
- E5 outcome: model loaded in 35.721 seconds; two 384-dimensional normalized embeddings using `query:` and `passage:` prefixes produced cosine similarity 0.9337.
- Resource outcome: single-process sequential peak RSS was 2575.0 MB; this is a smoke-test observation, not a steady-state benchmark.
- Blockers: no semantic NER label mapping was available in the tested checkpoint config; gated `ai4bharat/IndicNER` was not accessed.
- Artifact: `data/manifests/model_smoke_tests.json`.
- Decision: retain all candidate selections as `null`; smoke tests do not justify a winner. Next step is deterministic number/date checking and benchmark preparation with manually labelled data.

## 2026-10-26T12:00:00+05:30 — Deterministic fact checks
- Phase: deterministic numeric/date checks.
- Files added: `scripts/deterministic_checks.py`, `data/processed/xlsum/hindi_deterministic_checks.jsonl`, and `data/processed/xlsum/english_deterministic_checks.jsonl`.
- Commands run: compiled the checker; ran it against both XL-Sum pilot JSONL files; validated state/manifests as JSON; summarized review flags.
- Outcome: 120 records checked. Eight English and seven Hindi records were flagged because a date/number/percentage/currency expression in the reference summary was not found verbatim in the source extraction. The checker explicitly reports `review_required`; it does not classify records as false.
- Error/correction: a trailing comma introduced during state update made `PROJECT_STATE.json` invalid; it was corrected immediately and JSON validation passed.
- Next actions: prepare manually labelled NER/NLI gold examples from the pilots, resolve the tested NER label mapping or exclude that checkpoint from category scoring, and benchmark only on comparable gold data.

## 2026-10-26T11:47:30+05:30 — Final checkpoint validation
- Phase: evaluation preparation checkpoint.
- Commands run: validated `PROJECT_STATE.json` and all JSON manifests; compiled all scripts; checked for `.venv`, `venv`, or `virtualenv` directories; counted artifacts and measured workspace size.
- Outcome: all JSON artifacts are valid; all scripts compile; no virtual environment directories exist. The processed tree contains 136 pilot records plus 120 deterministic-check records; `data/` is approximately 349 MB including the two official XL-Sum archives.
- Current blockers: no authorized GupShup data access; MUTANT has no paired references/standard evaluation split; tested Hindi NER checkpoint has generic labels without semantic mapping; no human-labelled gold data exists yet; workspace is not a Git repository.
- Next actions: create or obtain manually adjudicated NER/NLI gold annotations without fabricating labels, resolve/exclude the NER mapping issue, then run comparable candidate benchmarks and only select models if evidence supports it.
