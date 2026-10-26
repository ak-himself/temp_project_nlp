"""Validate a completed or in-progress NLI benchmark review CSV."""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "evaluation" / "nli_comparison_benchmark.jsonl"
DEFAULT_REVIEW_PATH = ROOT / "evaluation" / "nli_benchmark_review.csv"
REQUIRED_SOURCE_COLUMNS = {
    "example_id",
    "split",
    "category",
    "language",
    "source_dataset",
    "source_record_id",
    "source_split",
    "evidence",
    "claim",
    "expected_label",
    "phenomenon",
    "claim_origin",
    "annotation_status",
    "annotation_notes",
}
REVIEW_COLUMNS = {
    "review_status",
    "final_label",
    "final_phenomenon",
    "rewrite_claim",
    "ambiguity_flag",
    "leakage_flag",
    "reviewer_id",
    "review_date",
    "review_notes",
    "adjudication_status",
}
STATUSES = {"", "approve", "rewrite", "reject"}
LABELS = {"", "entailment", "contradiction", "neutral"}
AMBIGUITY_VALUES = {"", "yes", "no"}
LEAKAGE_VALUES = {"", "yes", "no"}
ADJUDICATION_VALUES = {"not_needed", "pending", "resolved", "excluded"}


def load_source() -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    records = [
        json.loads(line)
        for line in SOURCE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return records, {record["example_id"]: record for record in records}


def nonempty(value: str | None) -> bool:
    return bool(value and value.strip())


def validate(review_path: Path) -> tuple[list[str], dict[str, Counter[str] | int]]:
    errors: list[str] = []
    source_records, source_by_id = load_source()
    try:
        with review_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing = (REQUIRED_SOURCE_COLUMNS | REVIEW_COLUMNS) - columns
            if missing:
                errors.append(f"Missing columns: {', '.join(sorted(missing))}")
            rows = list(reader)
    except (OSError, csv.Error) as exc:
        return [f"Could not parse review CSV: {exc}"], {}

    seen: set[str] = set()
    status_counts: Counter[str] = Counter()
    label_counts: Counter[str] = Counter()
    split_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    phenomenon_counts: Counter[str] = Counter()

    for row_number, row in enumerate(rows, start=2):
        example_id = row.get("example_id", "")
        prefix = f"row {row_number}"
        if not nonempty(example_id):
            errors.append(f"{prefix}: missing example_id")
            continue
        if example_id in seen:
            errors.append(f"{prefix}: duplicate example_id {example_id}")
        seen.add(example_id)
        source = source_by_id.get(example_id)
        if source is None:
            errors.append(f"{prefix}: unknown example_id {example_id}")
            continue

        for field in ("evidence", "claim"):
            if row.get(field, "") != source[field]:
                errors.append(f"{prefix}: original {field} changed")

        status = row.get("review_status", "")
        label = row.get("final_label", "")
        ambiguity = row.get("ambiguity_flag", "")
        leakage = row.get("leakage_flag", "")
        adjudication = row.get("adjudication_status", "")
        status_counts[status] += 1
        if label:
            label_counts[label] += 1
        split_counts[row.get("split", "")] += 1
        category_counts[row.get("category", "")] += 1
        phenomenon = row.get("final_phenomenon") or row.get("phenomenon", "")
        phenomenon_counts[phenomenon] += 1

        if status not in STATUSES:
            errors.append(f"{prefix}: invalid review_status {status!r}")
        if label not in LABELS:
            errors.append(f"{prefix}: invalid final_label {label!r}")
        if ambiguity not in AMBIGUITY_VALUES:
            errors.append(f"{prefix}: invalid ambiguity_flag {ambiguity!r}")
        if leakage not in LEAKAGE_VALUES:
            errors.append(f"{prefix}: invalid leakage_flag {leakage!r}")
        if adjudication not in ADJUDICATION_VALUES:
            errors.append(f"{prefix}: invalid adjudication_status {adjudication!r}")

        if status == "approve":
            for field in ("final_label", "final_phenomenon", "reviewer_id", "review_date"):
                if not nonempty(row.get(field)):
                    errors.append(f"{prefix}: approved row requires {field}")
        if status == "rewrite":
            for field in ("rewrite_claim", "final_label", "final_phenomenon"):
                if not nonempty(row.get(field)):
                    errors.append(f"{prefix}: rewritten row requires {field}")
        if status == "reject" and not nonempty(row.get("review_notes")):
            errors.append(f"{prefix}: rejected row requires review_notes")
        if ambiguity == "yes" and adjudication not in {"resolved", "excluded"}:
            errors.append(
                f"{prefix}: ambiguous row requires resolved adjudication or exclusion"
            )
        if leakage == "yes" and adjudication not in {"resolved", "excluded"}:
            errors.append(
                f"{prefix}: leakage-flagged row requires resolved adjudication or exclusion"
            )

    missing_ids = set(source_by_id) - seen
    if missing_ids:
        errors.append(f"Missing source examples: {len(missing_ids)}")
    if len(source_records) != 120:
        errors.append(f"Source benchmark has {len(source_records)} rows, expected 120")
    if len(rows) != len(source_records):
        errors.append(f"Review CSV has {len(rows)} rows, expected {len(source_records)}")

    counts = {
        "rows": len(rows),
        "status": status_counts,
        "label": label_counts,
        "split": split_counts,
        "category": category_counts,
        "phenomenon": phenomenon_counts,
    }
    return errors, counts


def print_report(errors: list[str], counts: dict[str, Counter[str] | int]) -> None:
    print(f"Rows: {counts.get('rows', 0)}")
    for name in ("status", "label", "split", "category", "phenomenon"):
        print(f"{name}: {dict(counts.get(name, {}))}")
    print(
        "Semantic labels, phenomenon accuracy, and leakage flags require human "
        "judgment; this validator checks structure and recorded review decisions."
    )
    if errors:
        print(f"Validation failures: {len(errors)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("Validation passed structurally; benchmark is not frozen.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_csv", nargs="?", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args()
    errors, counts = validate(args.review_csv)
    print_report(errors, counts)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
