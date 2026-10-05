# Three incidents, evidence, and recovery

These synthetic incidents teach causal investigation. Read the observations, write competing hypotheses, and choose the next discriminating measurement before opening the analysis. Separate mitigation from root-cause repair and verify user outcomes after both.

## Incident 1: the cache that took down the database

At 12:00, task-list p99 rises from 180 ms to eight seconds. API CPU remains moderate. Redis hit rate drops from 98% to 12%, PostgreSQL active queries rise sharply, and connection-pool wait grows. A Redis deployment happened at 11:59. No database schema changed. Clients retry twice on timeout.

**Your investigation.** Determine whether Redis is unavailable, cold, or evicting. Compare timeouts with true misses. Measure origin query rate and duplicate fills per key. Check whether retry traffic is included in the apparent request rate. Avoid increasing every pool before understanding the database's service capacity.

<details><summary>Analysis and response</summary>

The deployment removed warm cache state. Unbounded miss fallback turned a small origin workload into nearly full traffic, and retries amplified it. The database became a shared queue, so unrelated endpoints also suffered. The causal chain is cold cache → duplicate origin work → saturation → timeouts → retries, not simply “Redis was slow.”

Mitigate by bounding origin concurrency, reducing retry amplification, shedding optional lists, and serving approved stale values where available. Warm the most valuable keys gradually. Verify pool wait and user error rates fall without hiding failed operations. Repair with single-flight, TTL jitter, cache-outage load tests, and an explicit fallback budget. A bigger Redis instance alone does not fix the cold-start failure path.

</details>

**Follow-up exercise:** calculate origin amplification for 98% hit rate becoming 12% at unchanged offered traffic, then include two additional client attempts. State why real retry timing prevents one simple multiplier from describing every moment of the incident.

## Incident 2: fast SQL, slow API

A release adds a shipping-cost lookup to task export creation. API p95 becomes four seconds; database query spans remain under 30 ms. Database CPU is low, but every pool connection is occupied. Several sessions are idle in transaction. The external provider's p95 is three seconds. Scaling API replicas makes errors worse.

**Your investigation.** Inspect the span boundary: does SQL timing include pool acquisition? Read transaction ownership in the new path. Compare pool checkout duration with provider calls. Check whether all paths release the client on error/cancellation. Identify whether active transactions hold locks or old snapshots.

<details><summary>Analysis and response</summary>

The code opened a transaction, read data, called the provider, then updated the export and committed. Connections sat idle while waiting on the network. More API replicas multiplied pool demand without increasing database capacity. SQL execution was fast because most delay occurred before queries or between them.

Mitigate by rolling back or disabling the new path and bounding admission. Refactor the workflow so external work is outside a long database transaction, while preserving correctness through a version check/state machine. If the provider result can become stale, validate the relevant version before commit or use a durable asynchronous operation. Instrument acquisition and total checkout time separately. Test provider delay and failure, not just a mocked immediate response.

</details>

**Follow-up exercise:** design the replacement sequence when task data can change during the provider call. Explain why moving the call outside the transaction without a version policy creates a different bug.

## Incident 3: duplicate payment after a worker restart

A customer reports two charges. Logs show one business order, two worker attempts, and two provider request IDs. The first attempt timed out after 30 seconds; the worker restarted; the second attempt succeeded. A later provider callback confirms the first charge also succeeded. The queue advertises at-least-once delivery.

**Your investigation.** Compare logical operation ID, broker event ID, worker attempt ID, and provider idempotency key. Determine when local state was persisted and whether timeout was recorded as failure or unknown. Verify callback identity/signature and state-transition handling. Do not immediately replay the job again.

<details><summary>Analysis and response</summary>

Each worker attempt generated a new provider idempotency key. The local system treated timeout as confirmed failure, so redelivery created another externally distinct operation. Queue behavior was consistent with its contract. The missing guarantee was stable intent identity across attempts and an unknown-outcome reconciliation path.

Stop unsafe retries for affected operations, identify duplicates through provider references and ledger reconciliation, and follow an authorized correction/refund process. Preserve audit evidence. Repair by persisting a stable payment attempt identity, reusing its provider key, classifying unknown outcomes, and making callbacks idempotent. Test a provider success followed by lost response and duplicate callbacks. A distributed lock would not fix the crash-after-effect window by itself.

</details>

**Follow-up exercise:** define the state machine and alert for an operation unknown for 15 minutes. Include a case where the provider status API is unavailable too.

## Cross-incident method

For each incident, record: user impact, timeline, recent changes, competing hypotheses, discriminating evidence, mitigation, verification, durable repair, and a regression experiment. Keep observations separate from explanations. “CPU was 40%” is an observation; “CPU was not the bottleneck” requires checking core distribution, throttling, and the workload boundary.

Mitigation may deliberately reduce functionality to preserve core operations. Root-cause repair changes the failure behavior. A postmortem should include the enabling conditions—unbounded fallback, transaction ownership, unstable operation identity—rather than stopping at the trigger event.

## Exercises

1. **Debug:** For each incident, name one plausible but wrong fix and the evidence against it.
2. **Implementation:** Reproduce one scenario locally with controlled faults and capture a trace/metric timeline.
3. **Design:** Write a runbook with a stop condition and a user-facing verification query.
4. **Interview:** Explain one incident in five minutes: symptom, evidence, mechanism, mitigation, prevention.

<details><summary>Evaluation guide</summary>

Strong answers follow resource ownership and durable state, avoid equating timeout with failure, and test recovery. They distinguish short-term stabilization from permanent correction and include cleanup/reconciliation after service metrics recover.

</details>

## Further reading and connections

[Google SRE troubleshooting](https://sre.google/sre-book/effective-troubleshooting/), [AWS retry guidance](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/), and [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/). Revisit [cache failures](../07-caching/cache-failures.md), [server pools](../05-backend/server-architecture.md), [idempotency](../20-production-patterns/idempotency-and-deduplication.md), and [SLOs](../14-observability/slos-and-alerting.md).
