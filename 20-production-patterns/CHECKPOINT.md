# Checkpoint: Production patterns

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A paid workspace upgrade changes local state, charges a provider, updates a projection, and sends notifications. Requests and events may duplicate.

## Questions

1. Place idempotency, outbox, inbox, and provider reconciliation at their actual atomic boundaries.
2. Compare saga compensation with two-phase commit and explain which participants support each.
3. Decide whether CQRS/event sourcing helps and define projection/event evolution.
4. Review tenant isolation, soft deletion, audit, optimistic/pessimistic concurrency, and flags through the workflow.

## Evidence to produce

Draw the state machine and failure table, including an unknown payment outcome and a failed compensation.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Every pattern has a specific problem, cost, and reason not to use it. No local lock or transaction is claimed to cover unsupported external effects. Identity, retention, and repair are explicit.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
