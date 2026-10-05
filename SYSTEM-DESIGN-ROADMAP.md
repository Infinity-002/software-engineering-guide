# System design roadmap

Prerequisites: HTTP/APIs **P0**, relational modeling/transactions/indexes **P0**, authentication/authorization **P0**, caching/queues **P1**, and partial failure **P1**. Review the [main roadmap](ROADMAP.md) when a design depends on an unfamiliar mechanism.

Begin with [the fourteen-step method](19-system-design/methodology.md) **P0**. For every design, produce requirements, estimates, APIs, schema, read/write diagrams, bottlenecks, failure histories, consistency/security decisions, telemetry, and rejected alternatives. The sections below link to complete walkthroughs; use the named headings within each file.

## Stage A — One authority and one major data path

Design | Priority | Additional prerequisites | Main reasoning goal
--- | --- | --- | ---
URL shortener | P0 | Unique constraints, HTTP redirects, caches | Read-heavy scale, code collisions, takedown freshness
Pastebin | P0 | Text safety, retention, object storage basics | Separate content lifecycle from public/private visibility
Rate limiter | P0 | Atomic updates, clocks, token buckets | Define burst/fairness and distributed approximation
File upload service | P0 | Streaming, authorization, object capabilities | Publish only verified complete objects; repair partial work

Read [beginner designs](19-system-design/beginner-designs.md). Exit evidence: a working small implementation of one design and a failure experiment after each durable boundary.

## Stage B — Asynchronous and derived state

Design | Priority | Additional prerequisites | Main reasoning goal
--- | --- | --- | ---
Notification service | P1 | Outbox, retries, provider uncertainty | Distinguish accepted, attempted, and delivered
Chat system | P1 | WebSockets, durable cursors, membership | Recover missed live events without losing history
Search autocomplete | P1 | Prefix/inverted indexes, client request races | Bound hot-prefix work and protect private suggestions
Job queue | P1 | Reservations, idempotency, DLQs | Survive worker crashes and bounded backlog
Analytics pipeline | P1 | Streams, event time, sketches | Handle duplicates, lateness, replay, and approximate counts
Image hosting | P1 | Uploads, workers, CDN, content validation | Separate original authority from rebuildable variants

Read [intermediate designs](19-system-design/intermediate-designs.md). Exit evidence: explain which state is authoritative, which is a projection, and how every projection can be rebuilt safely.

## Stage C — Skew, coordination, and competing guarantees

Design | Priority | Additional prerequisites | Main reasoning goal
--- | --- | --- | ---
Twitter/X-style feed | P2 | Fanout, social graph, cache/privacy | Hybrid write/read fanout under celebrity skew
YouTube-style platform | P2 | Bulk storage, transcoding, CDN | Bandwidth, processing lifecycle, adaptive playback
Drive-style storage | P2 | Versions, chunks, sync, garbage collection | Concurrent offline edits and safe object lifecycle
Uber-style ride system | P2 | Spatial partitioning, state machines | Approximate location versus exclusive assignment
Collaborative editor | P2 | Causality, operation identity, OT/CRDT concepts | Convergence, durable save, offline history
Payment system | P2 | Transactions, idempotency, audit, sagas | Unknown provider outcomes and ledger reconciliation
Distributed task scheduler | P2 | Leases/fencing, clocks, outbox | Ownership transfer, missed runs, duplicate execution
Large-scale search | P2 | Inverted indexes, partitioning, projections | Fanout tail latency, freshness, relevance, permissions

Read [advanced designs](19-system-design/advanced-designs.md). Exit evidence: defend a design against a pause, partition, duplicate, stale authorization view, and recovery from backup. Explain why the guarantees still hold or where they deliberately weaken.

## Stage D — Specialist extensions

After Stage C, optional **P3** work includes implementing a miniature storage engine with crash recovery, model-checking a lease/epoch protocol, studying a consensus proof, evaluating an OT/CRDT implementation under generated operation histories, or building a search relevance evaluation set. These are deeper projects, not prerequisites for every engineering role.

## Review loop

Repeat one design with a changed requirement: tenfold peak, strict deletion, a region outage, a large tenant, or a tighter latency bound. Change only the components whose assumptions broke. End with a five-minute explanation of the most important trade-off and a measurement that could prove your design wrong. Use [case studies](21-case-studies/README.md) and [mock interviews](22-interview-preparation/mock-interviews.md) for synthesis.
