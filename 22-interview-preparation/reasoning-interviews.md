# Reasoning questions and evaluation rubrics

Answer with a mechanism, a concrete history, a failure case, and a trade-off. Define assumptions before naming a technology. The folded rubrics describe what a strong answer must address; they are not scripts to memorize.

## Frontend, JavaScript, and React

1. A search box shows results for an older query after the user types more. Explain the event-loop and application-state causes, then design cancellation/relevance handling.
2. A React list loses input state when sorted. Explain reconciliation, identity, and keys without saying React is “random.”
3. A page downloads quickly but typing is delayed. Distinguish network, JavaScript, layout, paint, and React work with measurements.
4. An effect submits a purchase whenever cart state changes. Explain why the trigger and retry semantics are wrong.
5. Server-rendered HTML contains a date that differs on the client. Explain hydration and the missing data/locale contract.
6. TypeScript says a response is `Task`, but production receives malformed JSON. Identify the runtime boundary and design validation.

<details><summary>Frontend rubric</summary>

Use request/query identity to reject stale completion; abort alone is not proof of remote cancellation. State belongs to stable tree identity, so keys must represent logical items. A performance trace locates main-thread work; a network waterfall alone cannot. Purchases belong to explicit intent with durable idempotency. Hydration requires compatible initial output. Types are erased and external bytes require runtime validation. Include accessibility and preservation of user input during failures.

</details>

## Backend and API reasoning

1. `POST /exports` times out, but an export later appears. How should retry and status lookup work?
2. API latency is high while SQL execution is fast. Explain pool wait, event-loop delay, locks, and external calls held inside transactions.
3. Offset pagination repeats records during concurrent inserts. Design a cursor with a stable tie-breaker and state its limits.
4. A webhook arrives three times and out of order. Define signature verification, identity, durable acceptance, and state-transition rules.
5. When does splitting a service improve the system, and when does it turn one invariant into a distributed transaction?

<details><summary>Backend rubric</summary>

Separate accepted, committed, responded, and observed states. A timeout can be an unknown outcome. Bound resources and release ownership on every path. Cursor pagination avoids shifting offsets but is not a snapshot under arbitrary mutations. Verify raw signed payload according to the protocol and enforce replay/authorization rules. Service boundaries should follow coherent ownership and concrete operational needs.

</details>

## Databases and caches

1. A query grows from 20 ms to three seconds as a table reaches 50 million rows. Give an investigation order before adding an index.
2. Two correct transactions leave no doctor on call. Explain write skew and compare serializable retry, a guard lock, and redesigning the invariant.
3. Why can an index-only scan still touch table pages in PostgreSQL?
4. A user writes to the leader and immediately reads old data. Offer several read-your-writes strategies with costs.
5. Redis improves latency, then users see stale account data. Draw at least one stale-fill race and distinguish permission data from cosmetic data.
6. One hundred thousand requests miss the same hot key. Explain coalescing, stale serving, jitter, and origin admission.

<details><summary>Database/cache rubric</summary>

Inspect actual query/parameters, plan estimates versus reality, buffers, locks, pool wait, and result size. Explain MVCC visibility and cross-row anomalies, not just “use transactions.” PostgreSQL visibility information affects heap access. Replicas introduce lag; delays are heuristics unless tied to a replication position. Cache consistency needs authority, key scope, freshness, and repair. An outage fallback must not flood the database.

</details>

## Networking and security

1. Explain typing a URL through useful pixels, including cached connections and browser rendering.
2. Why can HTTP/2 requests interfere after packet loss, and what changes with HTTP/3?
3. Login returns success but the next browser request has no session. Diagnose credentials mode, cookie scope, SameSite, and CORS separately.
4. A decoded JWT says `admin`. What facts remain unproven?
5. A server fetches user-provided URLs to create previews. Threat-model redirects, DNS, internal addresses, and resource exhaustion.
6. Why can CSRF change state even when the attacker cannot read the response?

<details><summary>Networking/security rubric</summary>

Follow layers and distinguish cold/reused paths. TCP ordering can block multiplexed HTTP/2 delivery; QUIC has independent streams but shared congestion. Browser CORS and cookie rules are different. JWT integrity, issuer, audience, lifetime, purpose, and current authorization all matter. SSRF exploits server privileges, and response-read restrictions do not undo requests already sent. Frontend controls are not authoritative security boundaries.

</details>

## Distributed systems and system data structures

1. A worker processes a job and crashes before acknowledgement. Where must deduplication occur?
2. Two machines believe they are leader. Why can that happen in a correct system, and what prevents conflicting commits?
3. A ten-second lease expires while its holder pauses. Explain fencing and its maximum-seen-token limitation.
4. Does `R + W > N` prove linearizability? State what it actually proves.
5. Explain CAP through a partitioned write/read history.
6. A Bloom filter says a key is absent. Under which assumptions is that safe?
7. Why do LSM trees sometimes stall after initially excellent write throughput?
8. How do Merkle trees find replica differences, and why can't they choose the authoritative value alone?

<details><summary>Distributed rubric</summary>

Place duplicate suppression atomically with the local effect and address external effects separately. Belief differs from authority; terms/quorums/fencing constrain accepted operations. Quorum intersection needs a protocol around it. CAP concerns partition-time linearizability and formal availability. Bloom negatives require complete insertion visibility and stable hashing. Compaction debt can exceed maintenance capacity. Merkle hashes locate disagreement but need versions/conflict rules for repair.

</details>

## Cloud, operations, and production debugging

1. Adding API replicas makes database errors worse. Explain fleet-wide pools and admission.
2. Kubernetes pods are Running but receive no traffic. Trace selectors, readiness, ports, and network policy.
3. A shared database outage triggers liveness restarts everywhere. Why is that harmful?
4. The backup job succeeds daily. What evidence establishes RPO/RTO?
5. A request takes five seconds across three services. Explain critical-path tracing, gaps, and why summing spans can mislead.
6. A canary is healthy but the full rollout fails. Discuss traffic representativeness, delayed work, and shared capacity.

<details><summary>Operations rubric</summary>

Measure resource demand across the fleet. Kubernetes status is not application correctness. Health checks have distinct purposes. Restore drills include data, keys, configuration, routing, and business validation. Traces connect work and waiting, while browser timing may lie outside server spans. Canary decisions require meaningful populations, budgets, and compatibility checks.

</details>

## Exercises

Choose one question per domain. Give a two-minute explanation, then a five-minute failure walkthrough with a diagram. Score each answer 0–3: 0 names only, 1 correct happy path, 2 failure mechanism and repair, 3 explicit assumptions, trade-offs, and validation. Revisit the linked curriculum until every P0 answer reaches at least 2 and your target specialty reaches 3.

## Further reading and connections

Use the repository's [coverage index](../COVERAGE.md) to locate the deep chapter for any missed mechanism. Continue to [mock interviews](mock-interviews.md), [incident cases](../21-case-studies/incident-lab.md), and the [interview roadmap](../INTERVIEW-ROADMAP.md). [Google SRE troubleshooting](https://sre.google/sre-book/effective-troubleshooting/) is useful practice for evidence-led explanations.
