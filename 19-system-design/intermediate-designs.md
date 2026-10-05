# Six production designs

These designs extend the [beginner set](beginner-designs.md) with asynchronous work, persistent connections, derived data, and operational recovery. Each uses the [fourteen-step method](methodology.md). Treat all scale figures as hypothetical inputs to challenge.

## Notification service

### Requirements and estimates — steps 1–4

Clarify channels, user preferences, urgency, scheduling, and the meaning of delivered. Assume email, push, and in-app notifications; transactional notices should be accepted quickly and attempted within one minute, while marketing can be delayed. Provider acceptance is not proof that a human saw the message.

At ten million notifications/day, average demand is about 116/s, but a campaign can create a million-message burst. Payload size may be modest while provider quotas and fanout dominate. Estimate per-channel peaks and retry amplification, not just the combined average.

### APIs, data, architecture — steps 5–7

Accept `POST /notifications` with recipient, template/version, safe parameters, channel policy, and operation ID. Store intent, preference decision/version, schedule, attempts, provider references, and terminal/unknown status. Expose status without leaking message contents to unauthorized callers.

```text
business outbox -> notification intake -> intent store + queue
  -> channel workers -> providers
provider callbacks -> verified status updates
```

Keep templates versioned so retries do not unexpectedly change content. Separate in-app durable notification state from ephemeral delivery attempts. Check whether preferences must be evaluated at enqueue time, send time, or both; a user can unsubscribe while a campaign waits.

### Bottlenecks and failure reasoning — steps 8–10

Partition work by channel/priority/tenant where needed, and enforce provider-specific concurrency/rate limits. A single queue can let a marketing burst delay password-reset messages. Use bounded retries with jitter, classify permanent failures, and route poison messages to a monitored DLQ.

A worker can send successfully and crash before recording success. Use provider idempotency where available; otherwise retain an unknown outcome and reconcile rather than promising exactly one message. Provider callbacks can duplicate or arrive out of order, so state transitions need identity and precedence rules. A delayed “accepted” callback must not revert a later “delivered” state.

### Consistency, security, telemetry, choices — steps 11–14

Durable intake plus at-least-once processing is a realistic baseline. Define which duplicates are tolerable and which channels support stronger suppression. Protect recipient data, verify callback signatures, bound template input, and prevent one tenant from using another's sender identity.

Measure event-to-attempt latency, provider acceptance/delivery outcomes, oldest pending age, retry/DLQ rates, and preference violations. Do not measure only worker success. A managed notification provider may remove operational work; a custom service is justified by policy, scale, integration, or control requirements. Kafka is unnecessary if retained multi-consumer history is not needed.

### Exercises

Design a campaign pause after 20% of messages have been sent. Explain which effects can be stopped, which cannot be undone, and how status remains truthful during provider uncertainty.

## Chat system

### Requirements and estimates — steps 1–4

Clarify room size, direct/group messaging, edits/deletes, offline history, ordering, read receipts, and end-to-end encryption. Assume private rooms up to 500 members, durable text history, near-real-time delivery, and per-room order. Presence is approximate; delivered and read receipts are separate user-visible claims.

Assume 100,000 concurrent connections and 5,000 messages/s at peak, averaging 1 KB before protocol overhead. Fanout to 50 recipients per message can produce 250,000 deliveries/s, making connection memory and outbound bandwidth major limits. Retention and media are separate estimates.

### APIs, data, architecture — steps 5–7

Use WebSocket commands with client message IDs, `GET /rooms/{id}/messages?after=cursor`, and explicit membership operations. Store room membership, durable messages, server order/version, and receipt state with bounded retention.

```text
client -> connection gateway -> message authority -> durable log/store
                                  |
                                  v
                             fanout routing -> connected gateways
reconnect -> history API -> messages after cursor
```

Persist before acknowledging durable send. Assign per-room order at the authority, and deduplicate `(sender, clientMessageId)` under the chosen scope. A live fanout event is a delivery hint; durable history supports recovery.

### Bottlenecks and failures — steps 8–10

Distribute connections across gateways and route messages to gateways with relevant subscribers. A huge room changes the problem into broadcast fanout and may need a different path. Bound buffers for slow clients, disconnect/recover through cursors, and jitter reconnects.

If persistence succeeds but fanout fails, reconnect/history fills the gap. If acknowledgement is lost, client retry returns the same durable message. Gateway failure loses connections, not history. Membership revocation must stop future delivery and prevent history access even when presence/subscription caches lag. Multi-region writes complicate room ordering; start with a home region per room unless requirements demand more.

### Consistency, security, telemetry, choices — steps 11–14

Promise order within a room, not globally across all rooms. Use stable cursors and explicit edit/delete events or versions. Authorize every join, send, and history read; validate browser WebSocket origin and session lifecycle. End-to-end encryption changes search, moderation, and key recovery and should be designed as a separate requirement.

Measure durable-send latency, live delivery delay, reconnect rate, cursor gaps, buffer pressure, and membership enforcement failures. SSE plus HTTP sends may suffice for simpler interactions. WebSockets improve bidirectional efficiency but require a long-lived connection operating model.

### Exercises

Simulate a gateway crash immediately after durable message commit. Show the sender and recipient recovery histories without duplication or permanent gaps.

## Search autocomplete

### Requirements and estimates — steps 1–4

Clarify whether suggestions are public terms, private task titles, personalized history, or full search results. Assume public vocabulary plus tenant-scoped task suggestions, top ten results, a 100 ms target under regional conditions, and updates visible within a minute. Permission changes require a stronger policy than ordinary relevance freshness.

At one million active search users making twenty queries/day, average traffic is about 231/s before keystroke multiplication. If each search emits five prefixes, that becomes about 1,160/s average. Debouncing and cancellation reduce waste but cannot be the server's only protection.

### APIs, data, architecture — steps 5–7

`GET /suggest?q=...&scope=...` returns bounded suggestions and stable IDs. Store normalized terms, popularity/freshness signals, tenant scope, and source version. Use a prefix index, trie/FST-like structure, or search-engine prefix facilities depending on corpus size and update requirements.

```text
source changes -> event/index pipeline -> suggestion index
browser -> suggestion API -> scoped index + hot-prefix cache
```

Normalize query and indexed content compatibly. A trie shares prefixes but can consume large memory; compact finite-state structures trade update flexibility for compact reads. Precomputed top candidates per prefix reduce query work while increasing update/storage cost.

### Bottlenecks and failures — steps 8–10

Short prefixes have huge candidate sets and high traffic. Require a minimum useful length where appropriate, cap work, and cache common public prefixes. Personalization/tenant scope increases cache cardinality and reduces sharing. Ranking should avoid a full scan/sort of every matching term per keystroke.

Index updates can arrive out of order, so use source versions. Rebuild into a new index generation, catch up, validate, then switch atomically through a pointer/alias. A failed pipeline should expose freshness age, not silently serve obsolete private titles forever. The UI must reject obsolete responses when a shorter earlier query finishes late.

### Consistency, security, telemetry, choices — steps 11–14

Eventual relevance updates are acceptable under the stated minute bound; access control still filters the right tenant and current visibility. Query logs can contain private text, so minimize/redact and restrict retention. Bound query length and complexity to resist expensive-input abuse.

Measure response latency by prefix length, zero-result rate, index lag, ranking quality, and stale-response UI incidents. Start with a database prefix query plus a suitable index for small corpora. Add a specialized search index when ranking, language analysis, or scale exceeds that model; do not introduce it solely because the feature says “search.”

### Exercises

Design a private task-title autocomplete that never returns another workspace's text. Compare index-time filtering, query-time filtering, and authoritative rechecks under revocation.

## Job queue

### Requirements and estimates — steps 1–4

Clarify job duration, scheduling, priorities, retries, cancellation, and side-effect guarantees. Assume durable jobs from milliseconds to ten minutes, at-least-once attempts, bounded retries, and visible terminal failure. Cancellation is best effort until a defined irreversible boundary.

At one million jobs/day and two seconds average processing, average demand is about 23 concurrent worker-seconds per second, before peaks and retries. A tenfold peak needs roughly 230 concurrent processing slots if each slot runs one such job. CPU/I/O mix and downstream limits determine whether that concurrency is feasible.

### APIs, data, architecture — steps 5–7

`POST /jobs` returns an operation ID; `GET /jobs/{id}` exposes state; cancellation records intent. Store job identity, type/version, payload reference, schedule, attempt count, lease/reservation, and result/error summary.

```text
producer -> job authority/queue -> bounded workers -> effects
                       ^              |
                       +-- retry/DLQ --+
```

A PostgreSQL job table with atomic claiming can be a good initial implementation. A broker becomes useful for throughput and delivery features. Long-running work should checkpoint progress rather than restart a huge operation blindly.

### Bottlenecks and failures — steps 8–10

Separate expensive/slow job classes to avoid head-of-line delay. Bound prefetch and worker concurrency. Visibility expiry or worker death causes redelivery; renew reservations only while valid and make effects idempotent. A process pause can create overlapping workers, so ownership alone is not proof of exclusive external execution.

Persist results before acknowledgement under the intended scope. Crash after effect but before acknowledgement produces another attempt. Poison messages need quarantine and redrive ownership. Cancellation arriving after an external effect may require compensation or a truthful “already completed” result, not pretending the effect vanished.

### Consistency, security, telemetry, choices — steps 11–14

The job state machine must reject stale attempt updates and retain stable effect identities. Authenticate producers, authorize payload resources, and avoid executing arbitrary serialized code from untrusted jobs. Worker credentials should be scoped to job classes.

Measure oldest eligible age, processing duration, attempts per completion, lease expiry, DLQ age, and downstream saturation. A queue smooths bursts but cannot sustain arrivals above capacity indefinitely. Prefer a simple database queue for moderate workloads; use a broker when its capabilities justify another operational dependency.

### Exercises

Design a ten-minute export with two-minute worker restarts, including checkpoints, ownership versions, cancellation, and duplicate final-publication prevention.

## Analytics pipeline

### Requirements and estimates — steps 1–4

Clarify whether reports need exact billing-grade counts or approximate product analytics, how late events may arrive, and whether deletion is required. Assume dashboard aggregates within five minutes, replayable history for 30 days, and explicit handling of duplicates/late events.

At 50,000 events/s and 500 bytes/event, raw ingress is about 25 MB/s or 2.16 TB/day in decimal units. Thirty-day raw retention is about 64.8 TB before compression, replicas, and metadata. This estimate makes batching, compression, retention, and storage tiering important immediately.

### APIs, data, architecture — steps 5–7

An ingestion API accepts bounded batches with event IDs, schema versions, event time, tenant, and attributes. Store immutable raw records or a durable stream, then build validated derived tables and aggregates.

```text
SDK/API -> durable stream -> validation/enrichment -> object archive
                              |
                              +-> windowed aggregates -> query store/dashboard
```

Partition to distribute load while preserving only necessary per-key ordering. Separate event time from processing time. Define a watermark/lateness policy: when is a window provisional, corrected, or final?

### Bottlenecks and failures — steps 8–10

Batching reduces per-event overhead but increases delay and retry batch size. Hot tenants/keys can overload partitions. Consumers must bound state for windows and deduplication. Approximate sketches such as HLL reduce distinct-count memory when exactness is not required.

Producer retries duplicate events. Consumers can crash between output and offset commit. Use scoped transactional processing where available or idempotent keyed updates/deduplication. Retention can expire before a lagging consumer catches up; snapshots and raw archives support recovery only if their schemas and positions remain usable.

### Consistency, security, telemetry, choices — steps 11–14

State whether dashboards are provisional and how corrections appear. Exact unique counts need different storage than approximate cardinality. Minimize personal data, authenticate tenant provenance, restrict query access, and design deletion across raw archives and derived stores.

Measure ingestion acceptance, data freshness, invalid-schema rate, partition skew, late-event rate, and reconciliation differences. A stream platform is justified by sustained volume/replay/independent consumers; a small product may start with batched database events. Avoid claiming “exactly once” without defining the output boundary and replay behavior.

### Exercises

An event arrives two days late and changes a previously displayed daily count. Define correction semantics, deduplication retention, and a dashboard explanation users can understand.

## Image hosting

### Requirements and estimates — steps 1–4

Clarify originals, variants, private access, transformations, moderation, and deletion. Assume durable originals, asynchronous thumbnails, public cacheable variants for opted-in content, and private workspace images. A processing failure must not lose the original.

At 500,000 images/day averaging 4 MB, originals add about 2 TB/day. Three variants averaging 200 KB add another 300 GB/day. Ten views per image can dominate egress. Estimate popular-image skew and conversion CPU separately.

### APIs, data, architecture — steps 5–7

Use upload intents and versioned object identities. Metadata records owner, visibility, original checksum/version, processing state, and named allowed variants. Serve a status endpoint and authorized image URLs.

```text
direct upload -> original/quarantine store -> queue -> transform workers
                                                    -> versioned variants
browser -> CDN -> public variants or authorized private path
```

Workers decode in constrained environments and produce deterministic variant names tied to source version and transformation policy. Publish only validated completed output. Keep originals immutable to simplify retry and regeneration.

### Bottlenecks and failures — steps 8–10

Decoding/transcoding is CPU/memory intensive; malicious dimensions can overwhelm workers despite small compressed files. Bound pixels, memory, duration, and supported formats. Autoscale workers within storage and queue limits. A transformation request with arbitrary dimensions can create infinite variants, so allowlist sizes or enforce quotas.

Worker crash leaves partial output; write to temporary/versioned keys and atomically publish metadata when complete. Duplicate jobs should converge on the same variant identity. CDN misses for a viral image can stampede the origin; cache immutable variants and coalesce generation if using on-demand processing.

### Consistency, security, telemetry, choices — steps 11–14

The original is authoritative; variants are rebuildable. Define deletion propagation across CDN, variants, originals, and backups. Private signed URLs have a revocation window; do not place private content under public cache keys. Strip metadata where privacy requires it and serve safe content types from an appropriate origin.

Measure upload-to-ready latency, failed transforms, queue age, cache hit rate, origin egress, and orphan variants. Eager processing gives predictable first-view latency but may waste work; on-demand processing saves unused variants but needs stampede and abuse controls. A managed image service can be simpler if its security, cost, and lifecycle model fit.

### Exercises

Design a policy change that regenerates thumbnails while old URLs remain live. Explain versioned keys, gradual backfill, cache reuse, and eventual cleanup.

## Exercises

Choose two designs and explain which shared mechanisms you would reuse and which guarantees differ. Produce a failure table and one measurable SLO for each. Then double one skew dimension—largest room, hottest prefix, longest job, largest tenant—and revise only the affected components.

<details><summary>Review rubric</summary>

Strong designs separate acceptance from completion, define durable identity and replay behavior, bound resource growth, and name the authority for state transitions. They include deletion/privacy and operational recovery, not just throughput. A queue, cache, or stream must have a stated purpose and failure policy.

</details>

## Further reading and connections

[Kafka design](https://kafka.apache.org/41/design/design/), [RabbitMQ acknowledgements](https://www.rabbitmq.com/docs/confirms), [Lucene](https://lucene.apache.org/core/), and [S3 object storage](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html). Review [queues](../09-messaging-streaming/queues-and-workers.md), [real-time/upload flows](../12-fullstack/realtime-and-uploads.md), [cardinality/search structures](../11-system-data-structures/hyperloglog.md), and [reliability](../13-reliability/resilience-and-recovery.md) before [advanced designs](advanced-designs.md).
