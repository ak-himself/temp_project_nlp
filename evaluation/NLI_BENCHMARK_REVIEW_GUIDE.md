# NLI Benchmark Human Review Guide

The review CSV is a working annotation sheet for the proposed benchmark. It is
not frozen until every retained example has been reviewed and the manifest has
been updated explicitly.

## Review each row

Read the exact `evidence` and the `claim` independently of the provisional
label and phenomenon. Then choose one action:

- `approve`: the pair and its label/tag are suitable as written.
- `rewrite`: the evidence is usable, but the claim, label, or phenomenon needs
  correction. Put the replacement claim in `rewrite_claim`.
- `reject`: the pair cannot be made reliable without inventing facts, or it is
  unusable because of ambiguity or leakage. Explain why in `review_notes`.

Preserve `evidence` and the original `claim` exactly. Never normalize,
translate, or silently edit source evidence.

## NLI labels

- **Entailment:** the evidence supports the claim as written, including its
  relevant entities, numbers, dates, polarity, and modality.
- **Contradiction:** the evidence supports a proposition incompatible with the
  claim. A changed number or date is a contradiction only when the evidence
  clearly establishes the original value.
- **Neutral:** the evidence neither supports nor contradicts the claim.

Unsupported information is usually **neutral**, not contradiction. For example,
if the evidence says that a meeting occurred but does not state its location,
a claim naming a location is neutral. It is contradiction only when the
evidence establishes an incompatible location or explicitly denies it.

## Phenomenon tags

Use a tag only when the relevant feature is actually present and meaningful:

- `number_change`: comparable quantities occur in evidence and claim, and the
  claim changes the value.
- `date_change`: comparable dates or temporal references occur and the claim
  changes the date.
- `entity_substitution`: the evidence establishes one entity and the claim
  names a specific incompatible alternative.
- `negation`: the claim explicitly denies or reverses the evidence proposition.
- `temporal_relationship`: both texts make comparable timing or ordering claims.
- `unsupported_claim`: the claim adds information not established by evidence
  without directly contradicting it.
- `paraphrase`: a genuine meaning-preserving rewording, not a verbatim copy.

If a claim repeats the evidence nearly word for word, consider a
`direct_restatement` tag rather than `paraphrase`.

## Important safeguards

- Flag ambiguous wording with `ambiguity_flag=yes` and add review notes.
- Flag possible same-event or near-duplicate leakage with
  `leakage_flag=yes`.
- Do not mark an ambiguous row approved without resolved adjudication or an
  explicit exclusion decision.
- Keep development and held-out test rows separate.
- Never use held-out test examples to choose a model, tune thresholds, or
  revise evaluation rules.
- Roman Hinglish remains untested unless genuine records are added and reviewed.

The validator checks structure and recorded decisions. It cannot determine
whether a label, phenomenon, or leakage judgment is semantically correct;
those decisions require human review.
