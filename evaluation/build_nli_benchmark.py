"""Build the proposed, human-reviewable NLI comparison benchmark.

The source evidence is copied from existing pilot records. Claims are
newly authored proposal text and remain pending human review.
"""

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = OUTPUT_DIR / "nli_comparison_benchmark.jsonl"
MANIFEST_PATH = OUTPUT_DIR / "nli_comparison_benchmark_manifest.json"

CATEGORIES = (
    ("english", "data/processed/xlsum_pilot/english.jsonl"),
    ("hindi", "data/processed/xlsum_pilot/hindi.jsonl"),
    ("code_mixed", "data/processed/mutant_pilot/code_mixed.jsonl"),
)
LABELS = ("entailment", "contradiction", "neutral")
PHENOMENA = (
    "paraphrase",
    "entity_substitution",
    "number_change",
    "date_change",
    "negation",
    "unsupported_claim",
    "temporal_relationship",
)


def load_records(relative_path: str) -> list[dict[str, str]]:
    path = ROOT / relative_path
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def first_evidence(text: str) -> str:
    """Return one exact, non-empty sentence or the complete source text."""
    stripped = text.strip()
    match = re.search(r"[.!?।]+", stripped)
    if match:
        return stripped[: match.end()]
    return stripped


def claim_for(evidence: str, label: str, category: str, phenomenon: str) -> str:
    if label == "entailment":
        if phenomenon == "paraphrase":
            return f"The report says the following: {evidence}"
        if phenomenon == "number_change":
            return "The report includes the same quantity described in the evidence."
        if phenomenon == "date_change":
            return "The report includes the same date described in the evidence."
        if phenomenon == "temporal_relationship":
            return "The event is described with the same timing as in the evidence."
        return evidence
    if label == "contradiction":
        if phenomenon == "entity_substitution":
            return "The event involved a different country from the one named in the evidence."
        if phenomenon == "number_change":
            return "The reported quantity was different from the one stated in the evidence."
        if phenomenon == "date_change":
            return "The event happened on a different date from the one stated in the evidence."
        if category == "english":
            return f"It is not true that {evidence[0].lower()}{evidence[1:]}"
        return f"यह सही नहीं है कि {evidence}"
    if category == "english":
        return "The evidence does not state whether the event involved a different country."
    if category == "hindi":
        return "इस साक्ष्य में किसी अलग देश के बारे में जानकारी नहीं दी गई है।"
    return "इस साक्ष्य में किसी अलग देश के बारे में जानकारी नहीं दी गई है।"


def build_cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    records_by_category = {
        category: load_records(path) for category, path in CATEGORIES
    }

    for category, _ in CATEGORIES:
        records = records_by_category[category]
        if len(records) < 40:
            raise ValueError(f"{category} needs at least 40 source records")
        for index, record in enumerate(records[:10]):
            evidence = first_evidence(record["text"])
            if not evidence or evidence not in record["text"]:
                raise ValueError(f"Could not preserve evidence for {record['id']}")
            for label_index, label in enumerate(LABELS):
                phenomenon = PHENOMENA[(index * 3 + label_index) % len(PHENOMENA)]
                cases.append(
                    {
                        "example_id": f"dev-{category}-{index + 1:02d}-{label}",
                        "split": "development",
                        "category": category,
                        "language": record["language"],
                        "source_dataset": (
                            "LingoIITGN/MUTANT"
                            if category == "code_mixed"
                            else "csebuetnlp/xlsum"
                        ),
                        "source_record_id": record["id"],
                        "source_split": record["split"],
                        "evidence": evidence,
                        "claim": claim_for(evidence, label, category, phenomenon),
                        "expected_label": label,
                        "phenomenon": phenomenon,
                        "claim_origin": "newly_authored_from_source_evidence",
                        "annotation_status": "awaiting_human_review",
                        "annotation_notes": None,
                    }
                )

        test_labels = (
            ("entailment", "paraphrase"),
            ("contradiction", "entity_substitution"),
            ("neutral", "unsupported_claim"),
            ("entailment", "number_change"),
            ("contradiction", "date_change"),
            ("neutral", "negation"),
            ("entailment", "temporal_relationship"),
            ("contradiction", "number_change"),
            ("neutral", "entity_substitution"),
            ("entailment", "paraphrase"),
        )
        for index, (label, phenomenon) in enumerate(test_labels):
            record = records[10 + index]
            evidence = first_evidence(record["text"])
            if not evidence or evidence not in record["text"]:
                raise ValueError(f"Could not preserve evidence for {record['id']}")
            cases.append(
                {
                    "example_id": f"test-{category}-{index + 1:02d}",
                    "split": "held_out_test",
                    "category": category,
                    "language": record["language"],
                    "source_dataset": (
                        "LingoIITGN/MUTANT"
                        if category == "code_mixed"
                        else "csebuetnlp/xlsum"
                    ),
                    "source_record_id": record["id"],
                    "source_split": record["split"],
                    "evidence": evidence,
                    "claim": claim_for(evidence, label, category, phenomenon),
                    "expected_label": label,
                    "phenomenon": phenomenon,
                    "claim_origin": "newly_authored_from_source_evidence",
                    "annotation_status": "awaiting_human_review",
                    "annotation_notes": None,
                }
            )
    return cases


def validate(cases: list[dict[str, object]]) -> dict[str, object]:
    if len(cases) != 120:
        raise ValueError(f"Expected 120 cases, found {len(cases)}")
    if len({case["example_id"] for case in cases}) != len(cases):
        raise ValueError("Example IDs are not unique")

    source_records = {
        category: {
            record["id"]: record
            for record in load_records(path)
        }
        for category, path in CATEGORIES
    }
    for case in cases:
        category = case["category"]
        record = source_records[category][case["source_record_id"]]
        if case["evidence"] not in record["text"]:
            raise ValueError(f"Evidence is not an exact source substring: {case}")

    development_ids = {
        case["source_record_id"]
        for case in cases
        if case["split"] == "development"
    }
    test_ids = {
        case["source_record_id"]
        for case in cases
        if case["split"] == "held_out_test"
    }
    if development_ids & test_ids:
        raise ValueError("Source records leak between development and test")

    counts = Counter(
        (case["split"], case["category"], case["expected_label"])
        for case in cases
    )
    status_counts = Counter(case["annotation_status"] for case in cases)
    return {
        "total": len(cases),
        "split_counts": Counter(case["split"] for case in cases),
        "category_counts": Counter(case["category"] for case in cases),
        "label_counts": Counter(case["expected_label"] for case in cases),
        "split_category_label_counts": counts,
        "annotation_status_counts": status_counts,
        "development_source_record_count": len(development_ids),
        "held_out_source_record_count": len(test_ids),
        "source_record_overlap": 0,
    }


def main() -> None:
    cases = build_cases()
    summary = validate(cases)
    OUTPUT_PATH.write_text(
        "\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "status": "proposed_not_frozen",
        "description": (
            "Proposed NLI comparison benchmark. Evidence is copied exactly "
            "from source records; all claims and labels require human review."
        ),
        "example_count": summary["total"],
        "splits": {
            "development": 90,
            "held_out_test": 30,
        },
        "categories": ["english", "hindi", "code_mixed"],
        "roman_hinglish_status": (
            "untested; no genuine mostly_latin records are present in the "
            "current MUTANT pilot"
        ),
        "source_files": [
            "data/processed/xlsum_pilot/english.jsonl",
            "data/processed/xlsum_pilot/hindi.jsonl",
            "data/processed/mutant_pilot/code_mixed.jsonl",
        ],
        "label_counts": dict(summary["label_counts"]),
        "category_counts": dict(summary["category_counts"]),
        "split_counts": dict(summary["split_counts"]),
        "annotation_status_counts": dict(summary["annotation_status_counts"]),
        "split_category_label_counts": {
            "|".join(key): value
            for key, value in summary["split_category_label_counts"].items()
        },
        "provenance_checks": {
            "exact_evidence_substrings": True,
            "unique_example_ids": True,
            "source_record_overlap_between_splits": 0,
            "synthetic_source_evidence": False,
        },
        "review_requirements": [
            "Review every evidence/claim pair and expected label.",
            "Confirm that phenomenon tags accurately describe each pair.",
            "Replace weak or unnatural claims before model comparison.",
            "Approve the development/test split before calling this benchmark frozen.",
        ],
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
