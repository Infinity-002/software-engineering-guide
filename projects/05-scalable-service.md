# Project 5 — Scalable service

Evolve Relay with load balancing, Redis, database replicas, queues, observability, and rate limiting. This project requires evidence that the added components improve a stated workload while containing failure. A diagram with more boxes is not completion.

## Establish the baseline

Choose a reproducible workload: reads/writes, payload sizes, tenant/key skew, concurrent users, and arrival model. Seed enough data to exercise realistic query plans. Measure throughput, latency distribution, errors, pool wait, CPU/memory, and database work before changing architecture. State the hardware and tool limits so local numbers are not presented as universal capacity.

Define SLIs for task save, list latency, job timeliness, and attachment readiness. Set learning SLOs appropriate to your environment. Choose explicit freshness policies for caches and replicas. Preserve an authoritative write path and resource authorization.

## Add components one at a time

1. Put two or more API instances behind a local reverse proxy/load balancer. Verify stateless request handling, trusted headers, and graceful drain.
2. Add Redis only to a selected hot read path. Implement coalescing, TTL policy, and bounded outage fallback.
3. Add a PostgreSQL read replica in a disposable setup or a clearly documented replica test environment. Measure lag and implement a read-your-writes policy.
4. Keep asynchronous work in the queue with bounded workers and retry/DLQ controls from Project 3.
5. Add atomic rate limiting and a separate concurrency/admission bound. Test noisy-tenant fairness.
6. Instrument logs, metrics, traces, and a dashboard that connects request symptoms to resource saturation.

Do not add Kubernetes solely to pass the project. A local Compose/proxy environment can demonstrate the core mechanisms. Kubernetes is an optional P2 deployment extension after the service's contracts are proven.

## Failure campaign

Experiment | Required evidence
--- | ---
Cache unavailable/cold | Origin work remains bounded; critical paths retain defined behavior
Replica deliberately delayed | No undocumented read-your-writes violation on protected paths
API killed during request | Safe retries and no dependence on process-local authority
Worker killed after effect | Duplicate delivery does not duplicate protected effects
Database slowed | Bounded queues/pool waits, shedding, and useful alerts
One hot tenant | Other tenants retain an explicit share of capacity
Rolling mixed-version release | Compatible schema/events and controlled error rate
Backup restoration | Measured restore time and application invariant checks

Run controlled failures in isolated local/test infrastructure. Record start/end conditions, observed user impact, and recovery. Do not keep broadening tests once the stated concerns are resolved; use new evidence to decide further work.

## Delivery and recovery

Build one immutable artifact and promote it through a local staging/release process. Add a backward-compatible migration and demonstrate old/new versions coexist. Define rollback or roll-forward based on actual data changes. Restore a backup into a fresh environment and measure RPO/RTO against the recorded test scenario, including configuration and routing.

## Acceptance criteria

- [ ] A baseline and each incremental change have comparable workload/evidence reports.
- [ ] Every component has a measured bottleneck or explicit requirement and an outage policy.
- [ ] Traces separate admission/pool wait, SQL, dependencies, and response work.
- [ ] Rate limits are atomic within their stated scope; distributed approximation is documented.
- [ ] Cache and replica freshness are observable and match the chosen user contract.
- [ ] Failure experiments show bounded resource growth and correct durable state.
- [ ] A restore drill and mixed-version rollout have concrete verification results.
- [ ] A final design review identifies remaining limits and a justified next step.

## Exercises and review

Remove one component and explain the measured regression. Double only the hottest tenant's traffic and compare it with doubling uniform traffic. Write a five-minute incident explanation for the worst failure you found, including why your initial hypothesis was right or wrong.

<details><summary>Hints after implementation</summary>

Fleet-wide pools and downstream limits can dominate API scaling. Cache hit rate alone is not a success metric. A replica's process health does not establish freshness. Recovery includes delayed jobs and data reconciliation after HTTP latency returns to normal.

</details>

## Further reading and connections

[Relay evolution](../21-case-studies/relay-evolution.md), [reliability](../13-reliability/README.md), [observability](../14-observability/README.md), [CI/CD](../18-ci-cd/safe-delivery.md), and [system design methodology](../19-system-design/methodology.md). [Google SRE workbook](https://sre.google/workbook/table-of-contents/) supplies deeper operational exercises.
