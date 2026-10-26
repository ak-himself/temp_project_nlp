"""Export the proposed NLI benchmark to a human-review CSV."""

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "evaluation" / "nli_comparison_benchmark.jsonl"
OUTPUT_PATH = ROOT / "evaluation" / "nli_benchmark_review.csv"
REVIEW_COLUMNS = [
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
]


def load_records() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in SOURCE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def export_review_csv(output_path: Path, overwrite: bool) -> int:
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"{output_path} already exists; rerun with --overwrite to replace it"
        )

    records = load_records()
    if not records:
        raise ValueError("The source benchmark contains no records")

    source_columns = list(records[0])
    output_columns = source_columns + REVIEW_COLUMNS
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_columns, extrasaction="raise")
        writer.writeheader()
        for record in records:
            row = {column: record.get(column, "") for column in source_columns}
            row.update(
                {
                    "review_status": "",
                    "final_label": "",
                    "final_phenomenon": "",
                    "rewrite_claim": "",
                    "ambiguity_flag": "",
                    "leakage_flag": "",
                    "reviewer_id": "",
                    "review_date": "",
                    "review_notes": "",
                    "adjudication_status": "not_needed",
                }
            )
            writer.writerow(row)
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace an existing review CSV",
    )
    args = parser.parse_args()
    count = export_review_csv(OUTPUT_PATH, overwrite=args.overwrite)
    print(f"Exported {count} examples to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
