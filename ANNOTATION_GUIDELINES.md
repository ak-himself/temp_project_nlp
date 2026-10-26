# Annotation guidelines

These templates are for manually labelled validation data. They are not model
predictions and must not be used to claim definitive factuality.

## NER

Annotate entity mentions in the source text using character offsets with an
exclusive `end_char`. Use these categories:

- `PERSON`: a person or named individual.
- `ORG`: an institution, company, political party, team, or other organization.
- `LOC`: a place, geographic area, or facility used as a location.
- `DATE`: a calendar date, year, or named time period.
- `MONEY`: a monetary amount including its currency.
- `PERCENT`: a percentage expression.
- `NUMBER`: a non-monetary numeric quantity.
- `OTHER`: a stable named entity that does not fit the categories above.

Keep the exact source substring, including script and spelling. Annotate nested
mentions only when both spans are independently meaningful. Do not normalize
transliteration, silently correct spelling, or infer an entity that is not
written in the source. Use `adjudication_status` values `single`, `agreed`, or
`escalated`.

## NLI source-evidence/summary-claim pairs

Create one row for each independently checkable claim in a summary. Select the
smallest source passage that can support or challenge the claim, and copy both
texts exactly. Use exactly one label:

- `entailed`: the source passage supports the claim without a material
  contradiction.
- `contradicted`: the source passage conflicts with a material part of the
  claim.
- `neutral`: the passage is insufficient to decide the claim or the claim is
  not addressed.

`neutral` means insufficient evidence, not that the claim is false. Record
numbers, dates, percentages, and currencies exactly; do not treat a mismatch as
automatic contradiction unless the context makes the mismatch material.
Annotate the same pair independently before adjudication, and record
`single`, `agreed`, or `escalated` in `adjudication_status`.
