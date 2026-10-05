# Bounding failure and recovering service

Relay's database slows from 20 ms to two seconds. Requests accumulate, clients retry, connection pools fill, and even healthy endpoints fail. The original slowdown becomes a system-wide outage because work was allowed to multiply without bounds.

## Timeouts are resource budgets

Set deadlines for the whole user operation, then allocate time across connection establishment, pool acquisition, and dependency calls. A two-second end-to-end deadline cannot support three sequential two-second dependency waits. Propagate remaining time where possible and cancel work that is no longer useful, while recognizing that cancellation may not undo a committed effect.

Choose timeouts from measured latency distributions and acceptable false timeouts, with margin for cold starts and network paths. Too short creates retries during ordinary variation; too long retains useless work and delays recovery. A timeout means outcome unknown unless the protocol provides stronger evidence.

## Retries can multiply load

If each of three nested layers makes up to three attempts, one user operation can generate up to 27 downstream attempts. Retry in the layer that understands the operation's semantics and deadline. Use a maximum attempt count, elapsed-time budget, retryable-error classification, and a retry budget relative to original traffic.

Exponential backoff increases waiting between attempts. Full jitter can choose a random delay from zero to a capped exponential bound, spreading synchronized clients. Without jitter, thousands of clients may retry at the same times and create repeated load waves. Retry only operations whose effects are safe under repetition or protected by [idempotency](../20-production-patterns/idempotency-and-deduplication.md).

## Isolate and reject before collapse

A circuit breaker stops calls after a failure pattern crosses a policy threshold, then cautiously probes recovery. It avoids repeatedly consuming time on a failing dependency, but needs suitable thresholds and can complicate recovery if all clients probe together. A bulkhead isolates capacity, such as separate worker pools for interactive requests and reports, preventing one workload from consuming everything.

Rate limiting constrains arrivals over time. Concurrency limiting bounds simultaneous work. Load shedding rejects work when the system cannot meet useful service. These are related but different: a slow dependency can exhaust concurrency at an ordinary request rate. Prefer early explicit overload responses to accepting work that times out after consuming scarce resources.

Graceful degradation removes optional work while preserving core behavior: show tasks without recommendations, defer analytics, or serve safe stale public content. Never degrade an authorization check into “allow” merely to keep success metrics green.

## Health checks and shutdown

Readiness asks whether this instance should receive new traffic. Liveness asks whether restarting this process is likely to help it recover. Startup probes give slow initialization time before ordinary health policy applies. A liveness check that fails whenever a shared database is down can restart every healthy API process and amplify the outage.

Graceful shutdown marks the instance unready, accounts for routing propagation, stops new work, drains bounded in-flight requests/jobs, and exits. A final forced kill must remain safe. Readiness is not instantaneous removal from all clients; keep-alive connections and discovery caches can lag.

## Redundancy has correlated failures

Two replicas on one host share host failure. Three zones can still share a bad deployment, credentials, control plane, or operator action. If independent serial dependencies each have availability `a_i`, a rough combined availability is the product `∏a_i`; independence is a strong assumption. Parallel redundancy improves some failures only when detection, failover, capacity, and shared dependencies work.

At 99.9% time availability, a 30-day month allows about 43.2 minutes unavailable. Request-based availability can produce a different result, especially during traffic peaks. State the SLI definition rather than quoting “three nines” without a denominator.

## Backups and disaster recovery

RPO is the targeted maximum acceptable data-loss window; RTO is the targeted time to restore useful service. An asynchronous replica lagging five seconds does not alone establish a five-second RPO across every disaster. Backups, WAL retention, region failure, encryption keys, and operational procedures all matter.

Run restore drills: provision an isolated target, restore data, apply required logs, validate invariants, restore secrets/configuration, switch routing, and verify user journeys. Measure the whole process. Protect backups against the same credentials or deletion mechanism that can destroy primary data. A backup never restored is unproven recovery evidence.

## Exercises

1. **Predict:** Every API retries three times during a database slowdown. Estimate amplification with two retrying downstream layers.
2. **Design:** Allocate an 800 ms request deadline across admission, two sequential dependencies, and response work.
3. **Debug:** A database outage triggers constant pod restarts. Explain the health-check mistake.
4. **Implementation:** Inject dependency latency and demonstrate bounded in-flight work, jittered retries, and deliberate shedding.
5. **Interview:** Give a restore plan with explicit RPO/RTO and explain what a replica does not protect against.

<details><summary>Hints</summary>

Multiplication gives a worst-case attempt bound when each layer retries independently. Reserve time for cleanup/response rather than assigning the entire deadline to one dependency. Recovery includes routing, keys, and validation, not just copying bytes.

</details>

## Further reading and connections

[AWS timeouts, retries, and jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/), [Google SRE cascading failures](https://sre.google/sre-book/handling-overload/), and [Google SRE data integrity](https://sre.google/sre-book/data-integrity/). Continue to [rate limiting](rate-limiting.md), [SLOs](../14-observability/slos-and-alerting.md), and [Linux shutdown](../02-operating-systems-linux/linux-debugging.md).
