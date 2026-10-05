# Checkpoint: Backend and API engineering

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

Task creation times out, but the task appears later. Listing repeats items during concurrent inserts, and SQL spans are fast while total API latency is high.

## Questions

1. Define accepted, committed, responded, and observed states, including retry-safe operation identity.
2. Design resource authorization, validation, safe errors, and transaction ownership.
3. Replace shifting offsets with a stable cursor and state what it does not guarantee.
4. Measure admission/pool wait separately from query execution and external dependency time.

## Evidence to produce

Write an API contract and a concurrent integration test using a real disposable database.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

A timeout is not rollback. The service enforces business invariants; the database arbitrates shared constraints. Cursor order includes a unique tie-breaker, and resource budgets apply across replicas.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
