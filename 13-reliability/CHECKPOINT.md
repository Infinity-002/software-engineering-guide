# Checkpoint: Reliability engineering

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A dependency slows tenfold. Retries synchronize, pools fill, liveness checks restart healthy processes, and a rate limiter becomes unavailable.

## Questions

1. Allocate an end-to-end deadline and bound attempts, concurrency, and queueing.
2. Compare backoff/jitter, circuit breakers, bulkheads, shedding, and degradation by failure mechanism.
3. Choose rate-limiter algorithms and atomic distributed state, including fail-open/fail-closed behavior.
4. Separate readiness/liveness/startup and define safe drain.
5. State RPO/RTO and prove recovery with a restore drill.

## Evidence to produce

Inject latency and show bounded resource growth, useful rejection, and measured recovery.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Retries consume capacity and do not prove failure. Rate, concurrency, and backlog are different limits. Recovery includes data correctness and configuration, not merely a green process.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
