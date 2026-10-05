# Checkpoint: Delivery and change safety

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A release renames a database field while old replicas and delayed consumers still run. Rolling back the image does not restore service.

## Questions

1. Design expand/contract migration, bounded backfill, mixed-version reads/writes, and removal criteria.
2. Explain immutable artifact promotion, provenance, configuration, and CI credential boundaries.
3. Compare rolling, blue-green, and canary exposure using user-outcome verification.
4. Define feature-flag defaults/lifecycle and a rollback or roll-forward plan that accounts for data changes.

## Evidence to produce

Write a release plan with preconditions, stop criteria, recovery steps, and verification for old/new combinations.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Code rollback is not data rollback. Queues and caches extend compatibility windows. A successful deployment controller status is weaker than successful user journeys.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
