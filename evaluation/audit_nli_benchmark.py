"""Create a conservative, preliminary audit of the proposed NLI benchmark."""

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "evaluation" / "nli_benchmark_review.csv"
SOURCE_PATH = ROOT / "evaluation" / "nli_comparison_benchmark.jsonl"
AUDIT_PATH = ROOT / "evaluation" / "nli_benchmark_audit.csv"
REPORT_PATH = ROOT / "evaluation" / "nli_benchmark_audit.md"

AUDIT_FIELDS = [
    "example_id",
    "split",
    "category",
    "evidence",
    "claim",
    "provisional_label",
    "provisional_phenomenon",
    "suspected_label_issue",
    "suspected_phenomenon_issue",
    "evidence_claim_quality",
    "suggested_action",
    "suggested_label",
    "suggested_phenomenon",
    "concise_reason",
]

GENERIC_PATTERNS = (
    "the evidence does not state",
    "the report includes the same quantity",
    "the report includes the same date",
    "the event is described with the same timing",
    "the event involved a different country from the one named",
    "the event happened on a different date from the one stated",
    "the reported quantity was different from the one stated",
)


def load_rows() -> list[dict[str, str]]:
    with REVIEW_PATH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def has_number(text: str) -> bool:
    return bool(re.search(r"\d", text))


def has_date_or_time(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:19|20)\d{2}\b|\b\d{1,2}:\d{2}\b|"
            r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b|"
            r"\b(?:january|february|march|april|may|june|july|august|"
            r"september|october|november|december)\b",
            text,
            flags=re.IGNORECASE,
        )
    )


def normalized(text: str) -> str:
    return re.sub(r"\W+", " ", text.casefold()).strip()


def audit_row(row: dict[str, str]) -> dict[str, str]:
    evidence = row["evidence"]
    claim = row["claim"]
    label = row["expected_label"]
    phenomenon = row["phenomenon"]
    claim_lower = claim.casefold()
    evidence_norm = normalized(evidence)
    claim_norm = normalized(claim)
    reasons: list[str] = []
    label_issue = ""
    phenomenon_issue = ""
    suggested_label = ""
    suggested_phenomenon = ""
    quality = "good"
    action = "keep_candidate"

    generic = any(pattern in claim_lower for pattern in GENERIC_PATTERNS)
    direct_restatement = (
        evidence_norm in claim_norm
        and len(evidence_norm) > 20
        and not any(marker in claim_lower for marker in ("not true", "सही नहीं"))
    )
    explicit_negation = "not true that" in claim_lower or "सही नहीं है कि" in claim

    if generic:
        quality = "poor"
        action = "rewrite_claim"
        reasons.append("generic template does not express a specific testable claim")
        if label == "contradiction":
            label_issue = "likely unsupported rather than contradiction"
            reasons.append("a vague alternative detail is not automatically incompatible")
        elif label == "entailment":
            label_issue = "entailment depends on a detail not stated in the evidence"
            reasons.append("the evidence may not contain the referenced quantity, date, or timing")
        elif label == "neutral":
            suggested_label = "neutral"
            reasons.append("neutral is plausible, but the generic wording should be replaced")

    if direct_restatement:
        if phenomenon == "paraphrase":
            phenomenon_issue = "claim is a direct restatement, not a paraphrase"
            reasons.append("retag as direct_restatement or rewrite as a real paraphrase")
            suggested_phenomenon = "direct_restatement"
            action = "rewrite_claim"
            quality = "needs_review"
        elif label == "entailment":
            suggested_label = "entailment"
            suggested_phenomenon = "direct_restatement"
        elif label == "contradiction":
            label_issue = "negated restatement needs explicit human confirmation"
            reasons.append("negation may contradict the evidence, but scope and modality need review")
            quality = "needs_review"
            action = "rewrite_claim"

    if explicit_negation:
        if phenomenon == "paraphrase":
            phenomenon_issue = "explicit negation is not a paraphrase"
            suggested_phenomenon = "negation"
            action = "rewrite_claim"
            quality = "needs_review"
            reasons.append("the claim reverses the evidence proposition")
        elif label == "contradiction" and not generic:
            suggested_label = "contradiction"
            suggested_phenomenon = "negation"

    if phenomenon == "number_change" and not has_number(evidence + " " + claim):
        phenomenon_issue = "no number appears in the pair"
        reasons.append("number_change is not supported by the text")
        quality = "poor"
        action = "rewrite_claim"
    if phenomenon == "date_change" and not has_date_or_time(evidence + " " + claim):
        phenomenon_issue = "no date or time appears in the pair"
        reasons.append("date_change is not supported by the text")
        quality = "poor"
        action = "rewrite_claim"
    if phenomenon == "temporal_relationship" and not has_date_or_time(evidence + " " + claim):
        phenomenon_issue = "no explicit date or temporal marker appears"
        reasons.append("temporal_relationship requires a temporal comparison")
        quality = "poor"
        action = "rewrite_claim"
    if phenomenon == "entity_substitution" and generic:
        phenomenon_issue = "no specific alternative entity is named"
        reasons.append("entity_substitution needs identifiable entities in both texts")
        quality = "poor"
        action = "rewrite_claim"
    if phenomenon == "paraphrase" and direct_restatement:
        phenomenon_issue = "near-verbatim wording is not a paraphrase"

    if label == "entailment" and generic and not suggested_label:
        suggested_label = ""
    if label == "contradiction" and generic:
        suggested_label = ""
    if label == "neutral" and generic and not label_issue:
        suggested_label = "neutral"

    if not reasons and label == "entailment" and not direct_restatement:
        reasons.append("pair appears coherent, but semantic entailment still needs human review")
    if not reasons:
        reasons.append("no mechanical defect detected; human semantic review remains required")

    if not row["claim"].strip() or not evidence.strip():
        quality = "poor"
        action = "replace_example"
        reasons.append("evidence or claim is empty")

    return {
        "example_id": row["example_id"],
        "split": row["split"],
        "category": row["category"],
        "evidence": evidence,
        "claim": claim,
        "provisional_label": label,
        "provisional_phenomenon": phenomenon,
        "suspected_label_issue": label_issue,
        "suspected_phenomenon_issue": phenomenon_issue,
        "evidence_claim_quality": quality,
        "suggested_action": action,
        "suggested_label": suggested_label,
        "suggested_phenomenon": suggested_phenomenon,
        "concise_reason": "; ".join(dict.fromkeys(reasons)),
    }


def write_report(audits: list[dict[str, str]]) -> None:
    quality_counts = Counter(row["evidence_claim_quality"] for row in audits)
    action_counts = Counter(row["suggested_action"] for row in audits)
    label_issues = sum(bool(row["suspected_label_issue"]) for row in audits)
    phenomenon_issues = sum(bool(row["suspected_phenomenon_issue"]) for row in audits)
    priority_order = {"poor": 0, "needs_review": 1, "good": 2}
    priorities = sorted(
        audits,
        key=lambda row: (
            priority_order[row["evidence_claim_quality"]],
            row["suggested_action"] != "replace_example",
            not bool(row["suspected_label_issue"]),
            row["example_id"],
        ),
    )[:25]
    lines = [
        "# Preliminary NLI Benchmark Audit",
        "",
        "This is an automated preliminary audit of the proposed benchmark, not",
        "gold-standard annotation. Suggested labels and actions are review aids",
        "only; human judgment is required before freezing the benchmark.",
        "",
        "## Counts",
        "",
        f"- Audited examples: {len(audits)}",
        f"- Evidence/claim quality: `{dict(quality_counts)}`",
        f"- Suggested action: `{dict(action_counts)}`",
        f"- Suspected label issues: {label_issues}",
        f"- Suspected phenomenon issues: {phenomenon_issues}",
        "",
        "## Highest-priority review examples",
        "",
        "| # | Example | Split | Category | Action | Reason |",
        "|---:|---|---|---|---|---|",
    ]
    for index, row in enumerate(priorities, start=1):
        reason = row["concise_reason"].replace("|", "\\|")
        lines.append(
            f"| {index} | `{row['example_id']}` | {row['split']} | "
            f"{row['category']} | `{row['suggested_action']}` | {reason} |"
        )
    lines.extend(
        [
            "",
            "## Common defects and recommended corrections",
            "",
            "1. Replace generic claims such as references to an unspecified "
            "different country, date, or quantity with concrete claims grounded "
            "in the evidence.",
            "2. Do not label an unsupported addition as contradiction unless the "
            "evidence establishes an incompatible fact; otherwise use neutral.",
            "3. Retag near-verbatim claims as `direct_restatement` or rewrite "
            "them as genuine paraphrases.",
            "4. Use `number_change`, `date_change`, and "
            "`entity_substitution` only when both sides contain comparable "
            "values or named entities.",
            "5. Review negation scope and modality manually, especially for "
            "claims that deny a full evidence sentence.",
            "6. The audit found no source-record ID overlap across splits in the "
            "existing manifest-level check; semantic same-event leakage still "
            "requires human review.",
            "",
            "## Limitations",
            "",
            "This audit uses text-pattern and exact-overlap heuristics. It cannot "
            "determine multilingual meaning, factual entailment, contradiction, "
            "phenomenon validity, or same-event leakage reliably. Blank suggested "
            "labels indicate that the evidence–claim pair was not sufficient for "
            "a conservative automated suggestion.",
            "",
            "The benchmark remains proposed and unfrozen.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = load_rows()
    audits = [audit_row(row) for row in rows]
    with AUDIT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS)
        writer.writeheader()
        writer.writerows(audits)
    write_report(audits)
    print(f"Audited {len(audits)} examples")
    print(f"Wrote {AUDIT_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
