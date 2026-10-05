# Checkpoint: Observability and production diagnosis

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

Users see five-second requests, but the average server latency and CPU dashboards appear healthy. A small region has severe errors.

## Questions

1. Use logs, metrics, traces, and browser timing to locate the critical path and missing intervals.
2. Explain counters, gauges, histograms, percentiles, and why per-replica p99 values cannot be averaged.
3. Design RED/USE dashboards with bounded labels and protected sensitive data.
4. Define SLI/SLO/SLA, error-budget burn, and actionable multi-window alerts.

## Evidence to produce

Produce a slow-request timeline and an alert/runbook tied to a user outcome rather than one machine threshold.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Population, sampling, and measurement boundary are explicit. Waiting is instrumented separately from execution. The alert identifies impact, owner, action, and verification.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
