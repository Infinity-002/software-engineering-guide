# Checkpoint: Messaging and streaming

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A worker commits an effect and crashes before acknowledgement. Another consumer falls behind retention, and a poison event is retried continuously.

## Questions

1. Draw at-most-once and at-least-once crash windows and define any exactly-once claim's scope.
2. Explain publisher acceptance versus consumer acknowledgement and durable business completion.
3. Design retry classification, jitter, DLQ ownership, redrive, and backpressure.
4. Explain Kafka partition order, group assignments, offsets, rebalancing, retention, and schema evolution.

## Evidence to produce

Run a controlled crash after effect commit and prove duplicate delivery cannot repeat the protected local effect.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Progress is committed only after the intended boundary. Queue age and retention matter, and global order is not inferred from one topic. External provider effects require their own identity/reconciliation support.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
