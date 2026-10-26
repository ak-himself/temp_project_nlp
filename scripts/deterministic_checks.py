"""Flag source/summary numeric and date differences for human review."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FACT_PATTERNS = {
    "date": re.compile(
        r"\b(?:19|20)\d{2}\b|\b\d{1,2}[/-]\d{1,2}[/-](?:19|20)?\d{2}\b",
        re.UNICODE,
    ),
    "percentage": re.compile(r"(?<!\w)\d+(?:[.,]\d+)?\s*%", re.UNICODE),
    "currency": re.compile(
        r"(?:[$€£₹]\s*[\d,]+(?:\.\d+)?|[\d,]+(?:\.\d+)?\s*(?:USD|EUR|GBP|INR|रुपये|रुपया))",
        re.IGNORECASE | re.UNICODE,
    ),
    "number": re.compile(r"(?<![\w%])\d+(?:[.,]\d+)*(?![\w%])", re.UNICODE),
}


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower().replace(",", ""))


def extract_facts(text: str) -> dict[str, list[str]]:
    facts: dict[str, list[str]] = {}
    for kind, pattern in FACT_PATTERNS.items():
        values = [normalize(match.group(0)) for match in pattern.finditer(text)]
        facts[kind] = list(dict.fromkeys(values))
    return facts


def compare(source: str, summary: str) -> dict[str, Any]:
    source_facts = extract_facts(source)
    summary_facts = extract_facts(summary)
    missing: dict[str, list[str]] = {}
    for kind, values in summary_facts.items():
        absent = [value for value in values if value not in source_facts[kind]]
        if absent:
            missing[kind] = absent
    return {
        "source_facts": source_facts,
        "summary_facts": summary_facts,
        "review_required": bool(missing),
        "missing_summary_facts_in_source": missing,
        "interpretation": "A flag indicates a possible mismatch requiring human review; it is not an automatic factuality label.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_jsonl", type=Path)
    parser.add_argument("output_jsonl", type=Path)
    args = parser.parse_args()

    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.input_jsonl.open(encoding="utf-8") as source, args.output_jsonl.open("w", encoding="utf-8") as output:
        for line in source:
            record = json.loads(line)
            summary = record.get("reference_summary")
            if not isinstance(summary, str):
                continue
            result = {"stable_id": record["stable_id"], **compare(record["source"], summary)}
            output.write(json.dumps(result, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
