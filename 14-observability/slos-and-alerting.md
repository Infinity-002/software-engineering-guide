# SLIs, SLOs, and useful alerts

A service can have green CPU dashboards while users cannot save tasks. Reliability must be defined through useful outcomes, not merely machine health. An SLI measures a behavior, an SLO sets an objective for it, and an SLA is a contractual commitment with defined consequences.

## Define the denominator before the target

For Relay task creation, an availability SLI might be successful valid create operations divided by eligible create attempts. A latency SLI might be the fraction of eligible requests completed within 500 ms. Define exclusions carefully: excluding every inconvenient failure can make the metric meaningless. Track client-caused errors separately without hiding server misclassification.

Choose the measurement point. Load-balancer success can miss a broken response body or browser failure. Server-side and client-side signals answer different questions. A synthetic probe detects known journeys continuously; real-user telemetry reflects actual populations but can be incomplete when the client cannot report.

An SLO such as 99.9% successful requests over 30 days permits a 0.1% error fraction within that window. At one million eligible requests, that is 1,000 bad requests. Time-based and request-based budgets differ. Do not convert request errors into downtime minutes unless the SLI actually measures time availability.

## Error budgets guide decisions

The error budget is the permitted unreliability under the objective. It can inform release pace, resilience work, and risk-taking. It is not permission to ignore individual severe incidents or security/data-integrity failures. A tiny number of corrupt payments can matter more than a large number of harmless read retries even if both count as failed requests.

Burn rate compares observed bad-event rate to the allowed rate. For a 99.9% objective, the allowed error fraction is 0.001. If the observed fraction is 0.01, the budget is burning at 10 times the sustainable rate for the same population/window interpretation. At that rate, a 30-day budget would be consumed in roughly three days if sustained.

Use multiple windows to distinguish a short spike from sustained rapid burn. A fast-burn alert catches a severe incident quickly; a slower window catches persistent degradation. Minimum traffic and sample size matter for low-volume services. Avoid paging on a single ratio computed from one request without context.

## Page for action, dashboard for investigation

An alert should identify user impact or imminent loss of a critical guarantee and lead to a concrete action. High CPU alone may be normal efficient operation; growing saturation plus latency/errors is more actionable. Every page needs ownership, severity, a runbook, and a way to determine whether the mitigation worked.

Separate symptoms from causes. Page on failed task creation, then use pool/database metrics to investigate. If you page independently on every correlated downstream symptom, one incident generates a storm. Group related alerts and preserve the causal timeline.

## Incident handling is disciplined uncertainty

Assign an incident lead and keep a timestamped record of observations, hypotheses, actions, and outcomes. Stabilize the system with reversible changes when possible: roll back a bad release, shed optional traffic, or cap retries. Preserve evidence without delaying urgent mitigation. Avoid making several speculative changes simultaneously, because you lose the ability to tell which mattered.

Communicate impact, affected users, known facts, and the next update time. Do not claim a root cause from the first suspicious metric. After recovery, verify data correctness and delayed work, not just HTTP success. Backlogs, duplicate effects, and missed notifications can remain after latency returns to normal.

A useful postmortem explains the triggering event, enabling conditions, detection gaps, and corrective actions with owners and validation. Blaming the person who deployed code does not explain why tests, rollout controls, or capacity limits failed to contain it. The goal is changing the system's behavior under the next similar event.

## Exercises

1. **Design:** Define an SLI for task save, notification timeliness, and attachment availability, including denominator and measurement point.
2. **Calculate:** A 99.95% request-success SLO sees 0.5% failures. What is the burn rate?
3. **Debug:** An alert fires every night during a harmless batch job. Decide whether the threshold, SLI, or workload isolation is wrong.
4. **Implementation:** Write a one-page incident runbook with verification and rollback criteria.
5. **Interview:** Explain SLI, SLO, SLA, and error budget without treating them as synonyms.

<details><summary>Hints</summary>

The allowed fraction is 0.05%, so 0.5% is a 10x burn. Notification timeliness needs an event-to-delivery or event-to-provider-acceptance boundary stated explicitly. An SLA may use different exclusions and consequences from an internal SLO.

</details>

## Further reading and connections

[Google SRE service-level objectives](https://sre.google/sre-book/service-level-objectives/), [alerting on SLOs](https://sre.google/workbook/alerting-on-slos/), and [incident management](https://sre.google/sre-book/managing-incidents/). Connect to [telemetry](logs-metrics-traces.md), [reliability](../13-reliability/resilience-and-recovery.md), and [delivery](../18-ci-cd/safe-delivery.md).
