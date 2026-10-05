# Checkpoint: Case studies

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

Relay grows from one service to multiple replicas, a cache, workers, and search. A cache deployment triggers database overload while a worker duplicates an external effect.

## Questions

1. Explain the measured trigger and new failure mode for each architectural addition.
2. Separate mitigation, diagnosis, durable repair, and post-recovery reconciliation.
3. Choose evidence that distinguishes pool exhaustion, query slowness, and retry amplification.
4. Explain which stage a small team should stop at and why more components may reduce reliability.

## Evidence to produce

Write a decision ledger and a five-minute incident narrative with timeline, hypotheses, evidence, and regression experiment.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

The account follows causal mechanisms and durable state, not blame or technology names. It includes the user-visible verification that proves recovery and the remaining limits of the design.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
