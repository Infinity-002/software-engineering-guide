# Interview preparation roadmap

Prerequisite: basic programming and DSA. Interview preparation follows the main [ROADMAP](ROADMAP.md); it is not a substitute for implementing and debugging. P0 is must know, P1 is strong production reasoning, P2 is advanced, and P3 is optional specialist depth.

## Pass 1 — Explain one complete application

Read [the life of a request](12-fullstack/the-life-of-a-request.md) **P0**, [HTTP](03-networking/dns-tls-http.md) **P0**, [backend boundaries](05-backend/server-architecture.md) **P0**, [SQL/transactions](06-databases/transactions-and-mvcc.md) **P0**, and [trust](08-security/trust-and-authorization.md) **P0**. Draw a task save from user intent to pixels. Explain timeout after commit, current authorization, and connection-pool ownership.

Exit test: explain the path in five minutes and answer three “what if this crashes?” follow-ups without introducing a magical exactly-once guarantee.

## Pass 2 — Choose a role emphasis

Role | Priority sequence | Evidence
--- | --- | ---
Frontend | [JS](04-frontend/javascript-runtime.md) P0 → [TS](04-frontend/typescript-boundaries.md) P0 → [browser](04-frontend/browser-internals.md) P0 → [React](04-frontend/react-mental-model.md) P0 → [state](04-frontend/state-and-data-fetching.md) P1 → [rendering](04-frontend/rendering-architectures.md) P1 → [performance/testing](04-frontend/README.md) P1 | Accessible UI, race reproduction, profiler-based improvement
Backend | [APIs](05-backend/api-design.md) P0 → [indexes](06-databases/indexes-and-query-plans.md) P0 → [transactions](06-databases/transactions-and-mvcc.md) P0 → [caching](07-caching/README.md) P0/P1 → [queues](09-messaging-streaming/queues-and-workers.md) P1 → [patterns](20-production-patterns/README.md) P1/P2 | Real database concurrency test, safe retry, worker crash recovery
Full-stack | Frontend/backend P0 plus [auth flows](12-fullstack/authentication-and-data-flows.md) P0 and [real-time/uploads](12-fullstack/realtime-and-uploads.md) P1 | One complete project traced through browser, API, data, and infrastructure
Infrastructure/SRE | [Linux](02-operating-systems-linux/linux-debugging.md) P0 → [reliability](13-reliability/README.md) P1 → [telemetry](14-observability/README.md) P1 → [cloud](16-cloud/cloud-primitives.md) P1 → [Kubernetes](17-kubernetes/kubernetes-model.md) P2 → [delivery](18-ci-cd/safe-delivery.md) P1 | Incident diagnosis, bounded overload, restore and rollout evidence

Role emphasis changes repetition time, not the need to understand adjacent trust and data boundaries.

## Pass 3 — Reason about partial failure

Prerequisite: transactions, queues, and HTTP timeouts. Study [consistency/CAP](10-distributed-systems/partial-failure-and-consistency.md) **P1**, [quorums](10-distributed-systems/replication-and-quorums.md) **P2**, [leases/fencing](10-distributed-systems/leases-and-fencing.md) **P2**, and [logical time/consensus](10-distributed-systems/README.md) **P2**. Connect [Bloom filters](11-system-data-structures/bloom-filters.md) **P1**, [B+ trees](11-system-data-structures/b-plus-trees.md) **P1**, and [LSM trees](11-system-data-structures/lsm-trees.md) **P2** to workload costs.

Exit test: draw a stale lease-holder history, explain the protected resource's fence, and give the assumptions under which a Bloom negative is safe. Formal consensus proofs and storage-engine implementation are **P3** extensions after these explanations are reliable.

## Pass 4 — Design and diagnose

Follow the [system-design roadmap](SYSTEM-DESIGN-ROADMAP.md) **P0/P1/P2** and [incident lab](21-case-studies/incident-lab.md) **P1**. For each design, derive one estimate, one invariant, one failure table, and one SLI before choosing advanced components. For each incident, state two hypotheses and the next measurement that distinguishes them.

## Pass 5 — Timed retrieval and correction

Use [reasoning questions](22-interview-preparation/reasoning-interviews.md) **P1** and [four mocks](22-interview-preparation/mock-interviews.md) **P1**. Practice two-minute explanations followed by deeper adversarial follow-ups. Score mechanisms, correctness, assumptions, failures, trade-offs, and communication. Revisit a chapter and perform its exercise when you cannot explain a boundary; do not merely memorize the folded rubric.

A strong answer can say “that depends on the configured durability acknowledgement” and then explain the alternatives. An unsupported claim of certainty is weaker than a precise guarantee with stated limits.
