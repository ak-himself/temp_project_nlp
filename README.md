# FactIndic

## Factuality-Aware Summarization for Indic and Code-Mixed Languages

**Status:** This is the proposed project blueprint. It describes the
intended design; it does not claim that every component has already been
implemented or evaluated.

## 1. Project overview

FactIndic explores whether an explicit factuality-checking stage can
make generated summaries more faithful to their source text.

**Research question:** Can factuality-aware summarization reduce
unsupported or contradicted claims while preserving summary usefulness,
concision, and reasonable runtime?

Given an article, the planned system will: 1. Generate a baseline
summary. 2. Split the summary into independently checkable claims. 3.
find source evidence for each claim. 4. Estimate whether the evidence
supports, contradicts, or does not establish each claim. 5.
Conservatively flag or revise questionable claims without inventing
facts. 6. Compare the baseline and factuality-aware outputs using the
same examples.

An NLI model estimates consistency with the supplied source; it does not
prove objective truth.

## 2. Language scope

Keep these categories distinct and evaluate them separately:

  -----------------------------------------------------------------------
  Category                Description             Data plan
  ----------------------- ----------------------- -----------------------
  Hindi                   Hindi in Devanagari     XL-Sum Hindi

  English                 English in Latin script XL-Sum English

  Devanagari code-mixing  Hindi-English mixed     Find or create a
                          text, potentially using suitable permitted
                          mixed scripts           sample

  Roman Hinglish          Hindi-English mixed     Find or create a
                          text in Latin script    suitable permitted
                                                  sample
  -----------------------------------------------------------------------

A model being labelled "multilingual" does not prove it works well on
code-mixed or Roman Hinglish text.

## 3. Datasets

Inspect each dataset's current card, license, access conditions, schema,
and size before downloading it.

### 3.1 Primary paired summarization data: XL-Sum

-   Dataset:
    [csebuetnlp/xlsum](https://huggingface.co/datasets/csebuetnlp/xlsum)
-   Initial configurations: `hindi` and `english`.
-   Expected fields include article `text`, reference `summary`, and
    metadata such as `id`, `url`, and `title`.
-   Use: baseline generation and reference-based evaluation.
-   License reported in the inspected card: **CC BY-NC-SA 4.0**.
    Re-check the current terms before redistributing or using
    commercially.
-   Compatibility note: the legacy dataset script may not work with
    current `datasets` versions. Inspect the current files and use a
    supported loading method.
-   Split policy: use train for permitted development, validation for
    iteration/model selection, and keep test untouched until final
    evaluation. Preserve the original split on every record.

Start with a small, bounded sample rather than downloading or processing
the full dataset without a reason.

### 3.2 Code-mixed text candidate: MUTANT

-   Dataset:
    [LingoIITGN/MUTANT](https://huggingface.co/datasets/LingoIITGN/MUTANT)
-   License reported in the inspected card: **CC BY 4.0**; verify
    current terms.
-   Use: exploratory Hindi-English code-mixed input coverage.
-   Limitation: inspected metadata exposed text-only examples, without
    paired reference summaries or a standard summarization evaluation
    split.
-   Do not calculate reference-based summarization scores on it unless
    valid reference summaries exist. Do not invent references and treat
    them as gold.

### 3.3 Conditional candidate: GupShup

-   Project page:
    [GupShup](https://anishacharya.github.io/papers/gupshup/)
-   Repository:
    [midas-research/gupshup](https://github.com/midas-research/gupshup)
-   Potential use: Hindi-English conversational summarization.
-   Access limitation: the inspected repository directs users to request
    the data through a form. Obtain authorized access before using it.
-   License caution: a repository's software license does not
    automatically establish the dataset's license. Verify dataset terms
    separately.

### 3.4 Dataset rules

-   Record source URL, revision/retrieval date, license, configuration,
    split, stable ID, and preprocessing.
-   Keep raw data separate from processed data.
-   Do not mix test examples into training, annotation, or model
    selection.
-   Do not commit large archives, model weights, caches, secrets, or
    unnecessary generated files.
-   If license or access is unclear, pause until it is resolved.

## 4. Models

Start with one baseline summarizer and one NLI model. Add components
only when the basic pipeline works.

### 4.1 Summary generation

**Initial candidate:** Groq API with `openai/gpt-oss-20b`, if currently
available to the account.

-   Keep the provider and model name configurable.
-   Store the API key in `.env`; never print or commit it.
-   Compare baseline and factuality-aware prompts on the same inputs
    with comparable settings.
-   Record model ID, prompt version, parameters, output, latency, and
    API errors.
-   Cache responses to reduce repeated calls and cost.
-   Gemini can be a later optional provider; its availability must not
    block the baseline.
-   Do not fine-tune in the initial phase.

Example `.env` (placeholders only):

``` dotenv
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

### 4.2 NLI: claim/evidence consistency

Candidates: - Lightweight multilingual candidate:
[MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli](https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli) -
Larger comparison candidate:
[MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7) -
Deferred larger candidate:
[joeddav/xlm-roberta-large-xnli](https://huggingface.co/joeddav/xlm-roberta-large-xnli)

Map native model labels explicitly: - `entailment`: the evidence
supports the claim. - `contradiction`: the evidence materially conflicts
with the claim. - `neutral`: the evidence does not establish the claim
or is insufficient.

Inspect the model's actual `id2label` mapping; never assume a fixed
class order. NLI output is an estimate, not proof of truth.

### 4.3 NER: supporting entity checks

NER can help track names, places, and organizations, but it is not a
complete factuality checker.

Candidates: - Hindi:
[MichaelHuang/muril_base_cased_hindi_ner](https://huggingface.co/MichaelHuang/muril_base_cased_hindi_ner) -
Alternative Indic candidate:
[theanugrah/muril-indic-ner](https://huggingface.co/theanugrah/muril-indic-ner) -
English baseline:
[dslim/bert-base-NER](https://huggingface.co/dslim/bert-base-NER) -
[ai4bharat/IndicNER](https://huggingface.co/ai4bharat/IndicNER) only if
access and usage terms permit.

The Hindi MuRIL checkpoint's mapping was documented against HiNER
references. Its native BIO categories (for example, `B-PERSON`,
`I-PERSON`, `B-LOCATION`) are not automatically equivalent to generic
labels such as `DATE`, `MONEY`, or `PERCENT`. Use verified mappings; do
not guess.

Keep an NER candidate only after checking its label mapping, language
coverage, license/access, size, and performance on manually labelled
examples.

### 4.4 Evidence retrieval (optional)

Candidate:
[intfloat/multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small).

Use it only when sources are long enough to require retrieval. Follow
its required prefixes: `query:` for a claim/query and `passage:` for
source passages. Retrieve candidate evidence, then run NLI. Compare
retrieval against human-selected evidence on a small sample. Skip this
component when direct evidence selection is sufficient.

### 4.5 Selection rule

A successful download or smoke test only proves that a model runs.
Select a model only after comparable evaluation on the same labelled
examples. Do not begin with a large ensemble or claim a winner in
advance.

## 5. End-to-end workflow

``` text
Article/text
    |
    v
Record language/script category
    |
    v
Generate baseline summary
    |
    v
Split summary into atomic claims
    |
    v
Select/retrieve source evidence for each claim
    |
    v
Run NLI: entailment / contradiction / neutral
    |
    v
Flag or conservatively revise questionable claims
    |
    v
Save factuality-aware summary and claim-level results
    |
    v
Compare baseline and factuality-aware outputs
```

### Implementation phases

**Phase 1 --- Define:** confirm assignment requirements, research
question, input/output, language categories, and deliverables.

**Phase 2 --- Baseline:** load a small permitted set of source/reference
pairs, generate summaries with one model, and save
outputs/settings/latency.

**Phase 3 --- Factuality:** split summaries into claims, select
evidence, run NLI, and save claim-level predictions and scores.

**Phase 4 --- Revision:** define conservative rules for unsupported
claims. Prefer flagging or omitting uncertain claims over inventing
replacement facts.

**Phase 5 --- Human gold data:** manually label claims and evidence.
Keep model predictions separate from gold labels; record annotators and
adjudication.

**Phase 6 --- Evaluation:** compare both systems on the same examples;
keep final test examples untouched until the protocol is fixed.

**Phase 7 --- Report:** document data/model versions, prompts, settings,
metrics, limitations, and negative results.

## 6. Evaluation

Evaluate summary quality, factual consistency, and efficiency
separately.

### Summary quality

-   **ROUGE-1, ROUGE-2, ROUGE-L:** similarity to a valid reference
    summary.
-   **Summary length:** document whether length is measured in words or
    tokens.
-   **Compression ratio:** define explicitly, for example
    `summary token count / source token count`. Lower is not
    automatically better.
-   **BERTScore:** optional; justify the multilingual model and report
    limitations on code-mixed text.

ROUGE and BERTScore are not factuality metrics.

### Factuality

On human-annotated claim/evidence pairs, report: - Accuracy when
meaningful for the label distribution. - Per-class precision, recall,
and F1. - Macro-F1 and confusion matrix. - Predicted proportions of
entailment, contradiction, and neutral. - Human-labelled factual
consistency for baseline versus factuality-aware outputs where feasible.

Always report sample counts and class balance. Do not report
gold-standard precision/recall/F1 without valid human labels.

### NER

Report entity-level precision, recall, and F1 only with human-labelled
spans and a consistent, documented label scheme. Entity overlap alone
does not prove a summary is factual.

### Efficiency

Measure mean and median inference latency, model loading time
separately, device used, peak memory when practical, and API
requests/errors/cost where available. Report pilot results as
preliminary.

## 7. Human annotation requirements

### NER

For each entity, record: - Exact entity substring. - Inclusive
`start_char` and exclusive `end_char`. - Verified native HiNER label or
a documented conversion. - Annotator ID, notes, and adjudication status.

Check:

``` python
source_text[start_char:end_char] == entity_text
```

Do not create entity labels from model predictions.

### NLI

For each summary claim, record: - Exact claim text. - Smallest relevant
source evidence passage. - `entailment`, `contradiction`, or
`neutral`. - Annotator ID, rationale/notes, and adjudication status.

Neutral means the supplied evidence is insufficient; it does not
automatically mean false.

## 8. Technical requirements

### Environment

-   OS: CachyOS Linux (Arch-based).
-   Python: pyenv-managed **3.12.8**.
-   Use the existing interpreter, for example:

``` bash
PYENV_VERSION=3.12.8 python --version
PYENV_VERSION=3.12.8 python -m pip --version
```

**Project constraint: never create or use a virtual environment**
(`venv`, `.venv`, `virtualenv`, conda, etc.). Do not change the global
pyenv version just for this project.

### Expected packages

Install only what the current phase needs; check installed packages
first.

-   `openai`: Groq-compatible API client.
-   `python-dotenv`: local environment variables.
-   `datasets`: dataset loading where supported.
-   `transformers`: NER/NLI.
-   `torch`: model inference.
-   `sentence-transformers`: E5 retrieval if needed.
-   `rouge-score`: ROUGE.
-   `scikit-learn`: evaluation metrics.
-   `pandas`: optional CSV/JSONL handling.

Do not install TensorFlow, CUDA packages, or additional frameworks
unless a concrete need justifies them. CPU-first is acceptable
initially.

### Git and large files

Do not commit: - `.env` or credentials. - Dataset archives and large raw
datasets. - Model weights and model caches. - Virtual environments,
Python caches, temporary outputs, or generated reports that do not
belong in source control.

Keep source code, documentation, configuration examples, small
manifests, and approved annotation templates in Git. Verify ignore rules
and `git status` before committing.

Suggested `.gitignore` entries:

``` gitignore
# Secrets
.env
.env.*
!.env.example
*.pem
*.key

# Python
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Virtual environments (do not create one for this project)
.venv/
venv/
virtualenv/

# Datasets and generated data
data/raw/
data/processed/
data/downloads/
*.tar
*.tar.gz
*.tgz
*.zip
*.bz2
*.7z

# Model weights/caches
models/
checkpoints/
weights/
.cache/
.cache/huggingface/
huggingface_cache/
torch_cache/

# Generated outputs
outputs/
runs/
wandb/
*.log
```

Review ignore patterns before applying them: retain the README, code,
small manifests, annotation templates, and any small approved gold data
that should be versioned. Ignore rules do not remove files already
tracked by Git; tracked large files must be untracked separately.

## 9. Suggested folder structure

This is a target layout, not a requirement to create everything
immediately.

``` text
FactIndic/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── configs/
├── data/
│   ├── raw/           # downloaded datasets; ignored by Git
│   ├── processed/     # normalized data; usually ignored
│   ├── annotations/   # templates and approved gold labels
│   └── manifests/     # provenance and metadata
├── prompts/
│   ├── baseline_summary.md
│   └── factuality_aware_summary.md
├── src/factindic/
│   ├── data.py
│   ├── summarize.py
│   ├── claim_split.py
│   ├── evidence.py
│   ├── factuality.py
│   ├── revise.py
│   └── evaluate.py
├── tests/
├── outputs/           # generated outputs; ignored by Git
└── reports/
```

Create only the files needed for the current phase.

## 10. Reproducibility rules

-   Inspect existing files before editing or replacing them.
-   Make one small change at a time; run and understand it before moving
    on.
-   Record commands, decisions, dataset/model revisions, prompt
    versions, and errors.
-   Cache API results to reduce repeated calls and cost.
-   Check model/data size and disk space before downloads.
-   Never fabricate data, annotations, citations, or benchmark results.
-   Keep secrets out of logs and version control.
-   Preserve test-set isolation.
-   Use explicit, documented label mappings.
-   Prefer a simple working baseline over a complicated system that is
    difficult to explain.

## 11. Definition of done

-   [ ] Project requirements and scope are agreed.
-   [ ] Dataset licenses, access, schemas, and splits are documented.
-   [ ] A reproducible baseline runs on a small sample.
-   [ ] Inputs, outputs, prompts, settings, and latency are saved.
-   [ ] Claim segmentation and evidence selection work on sample cases.
-   [ ] NLI labels are mapped correctly and interpreted conservatively.
-   [ ] Human-annotated gold data exists for reported factuality
    metrics.
-   [ ] Baseline and factuality-aware outputs are compared on the same
    examples.
-   [ ] Results include sample counts, metrics, runtime, and
    limitations.
-   [ ] The report makes no unsupported claims about truth or
    performance.
-   [ ] Instructions match the implementation that actually exists.

## 12. Open decisions and limitations

1.  **Code-mixed reference summaries:** MUTANT was inspected as a
    text-only corpus; a valid code-mixed reference-summary dataset still
    needs to be selected or annotated.
2.  **Roman Hinglish:** actual coverage must be tested; multilingual
    tags alone are insufficient.
3.  **NER taxonomy:** native HiNER labels do not map one-to-one to every
    generic date/money/percentage category.
4.  **NLI domain mismatch:** models trained on general NLI may behave
    differently on Indic text, code-mixing, names, dates, and numbers.
5.  **Human review:** a small adjudicated gold set is required for
    credible factuality evaluation.
6.  **Availability:** model names, API quotas, dataset access, and
    package compatibility can change. Record the exact model and
    retrieval date.
7.  **Course requirements:** confirm the official assignment
    requirements before expanding the scope.

## First milestone

**Do only this first:** confirm the assignment requirements, inspect the
repository, verify Python 3.12.8, and run one small end-to-end baseline
summarization example. Do not implement the full pipeline, download
every candidate model, or build an ensemble before the baseline is
understood.
