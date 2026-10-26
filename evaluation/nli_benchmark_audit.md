# Preliminary NLI Benchmark Audit

This is an automated preliminary audit of the proposed benchmark, not
gold-standard annotation. Suggested labels and actions are review aids
only; human judgment is required before freezing the benchmark.

## Counts

- Audited examples: 120
- Evidence/claim quality: `{'needs_review': 18, 'poor': 63, 'good': 39}`
- Suggested action: `{'rewrite_claim': 81, 'keep_candidate': 39}`
- Suspected label issues: 42
- Suspected phenomenon issues: 66

## Highest-priority review examples

| # | Example | Split | Category | Action | Reason |
|---:|---|---|---|---|---|
| 1 | `dev-code_mixed-01-contradiction` | development | code_mixed | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; entity_substitution needs identifiable entities in both texts |
| 2 | `dev-code_mixed-02-entailment` | development | code_mixed | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; date_change is not supported by the text |
| 3 | `dev-code_mixed-03-entailment` | development | code_mixed | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; temporal_relationship requires a temporal comparison |
| 4 | `dev-code_mixed-04-contradiction` | development | code_mixed | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; date_change is not supported by the text |
| 5 | `dev-code_mixed-04-entailment` | development | code_mixed | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; number_change is not supported by the text |
| 6 | `dev-code_mixed-06-contradiction` | development | code_mixed | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; number_change is not supported by the text |
| 7 | `dev-code_mixed-08-contradiction` | development | code_mixed | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; entity_substitution needs identifiable entities in both texts |
| 8 | `dev-code_mixed-09-entailment` | development | code_mixed | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing |
| 9 | `dev-code_mixed-10-entailment` | development | code_mixed | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; temporal_relationship requires a temporal comparison |
| 10 | `dev-english-01-contradiction` | development | english | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; entity_substitution needs identifiable entities in both texts |
| 11 | `dev-english-02-entailment` | development | english | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; date_change is not supported by the text |
| 12 | `dev-english-03-entailment` | development | english | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing |
| 13 | `dev-english-04-contradiction` | development | english | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; date_change is not supported by the text |
| 14 | `dev-english-04-entailment` | development | english | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; number_change is not supported by the text |
| 15 | `dev-english-06-contradiction` | development | english | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; number_change is not supported by the text |
| 16 | `dev-english-08-contradiction` | development | english | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; entity_substitution needs identifiable entities in both texts |
| 17 | `dev-english-09-entailment` | development | english | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; date_change is not supported by the text |
| 18 | `dev-english-10-entailment` | development | english | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; temporal_relationship requires a temporal comparison |
| 19 | `dev-hindi-01-contradiction` | development | hindi | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; entity_substitution needs identifiable entities in both texts |
| 20 | `dev-hindi-02-entailment` | development | hindi | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; date_change is not supported by the text |
| 21 | `dev-hindi-03-entailment` | development | hindi | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; temporal_relationship requires a temporal comparison |
| 22 | `dev-hindi-04-contradiction` | development | hindi | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; date_change is not supported by the text |
| 23 | `dev-hindi-04-entailment` | development | hindi | `rewrite_claim` | generic template does not express a specific testable claim; the evidence may not contain the referenced quantity, date, or timing; number_change is not supported by the text |
| 24 | `dev-hindi-06-contradiction` | development | hindi | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; number_change is not supported by the text |
| 25 | `dev-hindi-08-contradiction` | development | hindi | `rewrite_claim` | generic template does not express a specific testable claim; a vague alternative detail is not automatically incompatible; entity_substitution needs identifiable entities in both texts |

## Common defects and recommended corrections

1. Replace generic claims such as references to an unspecified different country, date, or quantity with concrete claims grounded in the evidence.
2. Do not label an unsupported addition as contradiction unless the evidence establishes an incompatible fact; otherwise use neutral.
3. Retag near-verbatim claims as `direct_restatement` or rewrite them as genuine paraphrases.
4. Use `number_change`, `date_change`, and `entity_substitution` only when both sides contain comparable values or named entities.
5. Review negation scope and modality manually, especially for claims that deny a full evidence sentence.
6. The audit found no source-record ID overlap across splits in the existing manifest-level check; semantic same-event leakage still requires human review.

## Limitations

This audit uses text-pattern and exact-overlap heuristics. It cannot determine multilingual meaning, factual entailment, contradiction, phenomenon validity, or same-event leakage reliably. Blank suggested labels indicate that the evidence–claim pair was not sufficient for a conservative automated suggestion.

The benchmark remains proposed and unfrozen.
