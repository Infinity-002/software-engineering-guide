# Checkpoint: Caching

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A 99% hit-rate cache is lost during deployment. PostgreSQL collapses, and some recovered keys contain stale values despite a recent invalidation.

## Questions

1. Estimate origin amplification and identify where admission must be bounded.
2. Draw the stale-fill race around a database commit and cache deletion.
3. Compare coalescing, TTL jitter, negative caching, and safe stale serving.
4. Define cache keys and freshness for task summaries versus workspace permissions.

## Evidence to produce

Inject a cold-cache event and show bounded origin work plus a version/freshness policy for refills.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Hit rate alone is insufficient. The cache has an authority, representation identity, stale policy, outage policy, and repair path. A short TTL does not prove a bound if stale data is inserted late.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
