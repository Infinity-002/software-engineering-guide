# Relay: one service to a scalable application

Relay is the running example, a team workspace with tasks, comments, attachments, notifications, and activity feeds. This is a synthetic engineering case study. Its purpose is to explain what evidence causes architecture to change, not to imply every successful product must pass through every stage.

## Stage 1: establish one correct vertical slice

```text
Browser -> Backend -> PostgreSQL
```

Start with semantic forms, one Node service, and PostgreSQL. Store users, memberships, tasks, and sessions with constraints. A task mutation authenticates the user, checks membership, validates input, and commits a conditional update. Use parameterized queries, a bounded pool, safe errors, and structured logs from the start.

The important first capacity is cognitive: one authority and one deployment make failures easier to explain. A modular backend can separate tasks, identity, and attachments without introducing network boundaries. Project 1 proves transaction and permission behavior; Project 2 adds the React client and its server-state model.

**Failure that teaches the next lesson:** two editors overwrite each other. Fix with versioned updates and conflict UX. Adding Redis would not solve this invariant. A task save timing out after commit requires an operation identity and reconciliation, not merely a bigger server.

## Stage 2: add frontend engineering and horizontal API capacity

```text
React -> Load Balancer -> API replicas -> PostgreSQL
```

Measured CPU or availability requirements justify multiple API replicas. Move process-local session authority to an appropriate shared store, keep uploads off ephemeral local disks, and make per-request state explicit. The frontend distinguishes local draft state, URL filters, and server-state cache. Accessibility and performance remain first-class acceptance criteria.

**New failure:** ten replicas each create a pool of 50 connections, exhausting the database. Horizontal compute scaling multiplied a shared-resource demand. Set a fleet-wide connection budget, measure acquisition wait, and use admission limits. Load balancing did not make the database infinitely parallel.

**Rejected alternative:** microservices for every table. The application still benefits from local transactions and one clear ownership model. Split deployment only when independent scale, reliability, or team boundaries justify it.

## Stage 3: remove measured repeated work and slow side effects

```text
React -> CDN -> Load Balancer -> Backend
                                  |-- Redis
                                  |-- PostgreSQL
                                  `-- Queue -> Workers
```

Serve content-hashed frontend assets through a CDN. Add Redis for frequently reused task summaries with an explicit freshness policy. Keep permissions and critical invariants authoritative. Move email, exports, and attachment processing to workers because users can accept asynchronous completion.

Use a transactional outbox when a task commit must reliably trigger notifications. Workers acknowledge after durable local processing and tolerate duplicates. Upload bytes go to object storage under a scoped intent; scanning and transformations happen before publication.

**New failure:** a hot summary expires and thousands of requests regenerate it. Add local coalescing, safe stale serving where allowed, TTL jitter, and an origin concurrency budget. A global distributed lock may be unnecessary if duplicate regeneration is merely inefficient.

**New failure:** an email sends but acknowledgement is lost. The queue redelivers. Define provider idempotency or accepted duplicate risk and reconciliation. Calling the queue “exactly once” would hide the real boundary.

## Stage 4: independent projections and evidence-based scaling

```text
                    +---- CDN assets/media
Browser ------------+
                    v
                API gateway
                    |
               Load balancer
               /     |     \
            API-1  API-2   API-3
               \     |     /
                shared data paths
                 /    |     \
              Redis  DB     Kafka
                     |        |
                  replicas  projection/notification workers
```

Introduce a retained stream when search, analytics, and other independent consumers need replay and their own progress. A simple work queue can remain for job dispatch. The stream is not a mandatory replacement for every asynchronous operation.

Read replicas help read capacity, with routing for read-your-writes and sensitive authorization. Search is a rebuildable projection. Partition data only after query/index improvements, archiving, vertical capacity, replicas, and caching fail to meet measured needs. Large tenants may need dedicated placement or subpartitioning.

An API gateway becomes useful when several client-facing services need consistent routing/policy. It does not own all business authorization. The architecture diagram contains more components because specific requirements appeared; a smaller deployment can correctly stop at Stage 1 or 2.

## Stage 5: operate the system as a set of contracts

Define SLIs for task saves, notification delay, attachment readiness, and search freshness. Trace request and asynchronous operation identities. Alert on user-impacting budget burn and backlog age. Establish backups, restore drills, rollout controls, secret rotation, and incident ownership.

Containers package reproducible processes. A managed platform may be sufficient; Kubernetes is justified only when its scheduling and platform abstractions pay for their operational surface. Multi-zone deployment addresses some infrastructure failures, while compatible releases and tested recovery address correlated failures.

## A decision ledger

| Observed problem | First intervention | Evidence for a larger change |
|---|---|---|
| Slow task query | Inspect plan/index/payload | Sustained resource saturation after query fixes |
| Slow repeated reads | Cache selected representation | Measured reuse and tolerable freshness |
| Email delays request | Durable background work | Multiple independent replay consumers may justify a stream |
| API CPU saturated | Profile, bound work, add replicas | Independently hot module may justify extraction |
| One tenant dominates | Quotas and workload isolation | Dedicated placement/subsharding after measurement |
| Regional outage objective | Restore/failover design | Multi-region replication justified by explicit RPO/RTO |

## Exercises

1. **Design:** Choose a stage for a 5,000-user internal workspace and defend every component you omit.
2. **Predict:** Remove Redis from Stage 3 during peak load. What bounds prevent a database collapse?
3. **Debug:** Search, API, and notifications disagree about one task. Identify authority, versions, and lag at each boundary.
4. **Implementation:** Complete the [five projects](../projects/README.md) in sequence and keep a decision log with measured triggers.
5. **Interview:** Explain Relay's evolution in ten minutes using failures rather than a list of technologies.

<details><summary>Review criteria</summary>

Each added component resolves a named problem and introduces acknowledged costs. Correctness fixes precede scale mechanisms. The learner can remove a cache or rebuild a projection without losing authoritative facts and can explain the limits of acknowledged durability.

</details>

## Further reading and connections

[Google SRE simplicity](https://sre.google/sre-book/simplicity/), [AWS caching challenges](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/), and [PostgreSQL performance tips](https://www.postgresql.org/docs/current/performance-tips.html). Revisit [the request journey](../12-fullstack/the-life-of-a-request.md), [system design method](../19-system-design/methodology.md), and [incident lab](incident-lab.md).
