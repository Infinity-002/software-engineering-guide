# Eight advanced system designs

These hypothetical designs are inspired by familiar product categories, not descriptions of the private internals of named companies. Each follows the [fourteen-step method](methodology.md). The difficult part is preserving a useful contract while changing placement, ownership, or timing—not merely adding more servers.

## Twitter/X-style feed

### Clarify, require, estimate — steps 1–4

Clarify follow relationships, ranked versus chronological feeds, privacy, deletes, reposts, and freshness. Assume a follower feed with chronological fallback, moderate ranking, near-real-time posts, and enforceable private-account/block rules. Feed staleness of several seconds is acceptable; unauthorized content is not.

Assume ten million daily active users, two posts/user/day, and fifty feed reads/user/day. That is 20 million posts/day and 500 million feed reads/day, about 231 writes/s and 5,787 reads/s average. A post by someone with ten million followers creates a skew problem that averages hide. Fanout work is posts multiplied by eligible recipients, not simply post QPS.

### APIs, model, architecture — steps 5–7

Define `POST /posts`, follow/unfollow/block operations, and `GET /feed?cursor=...`. Store authoritative posts, author/visibility/version, social edges, and deletion state. Feed entries are derived references, not independent copies of the authority. Cursor semantics should bind ranking/session context if the order changes over time.

```text
post API -> post store + outbox -> fanout workers -> per-user feed entries
feed API -> feed entries + selected author streams -> rank/hydrate -> response
```

Start with fanout-on-read: retrieve recent posts from followed authors and merge. It avoids writing millions of feed entries for inactive users. When read cost dominates, precompute feeds for ordinary authors. Treat very high-fanout authors separately and merge their recent posts at read time. The threshold should follow measured read/write cost and activity, not a magic follower count.

### Bottlenecks, scaling, failures — steps 8–10

Partition posts and social edges by access pattern; cache hot post bodies while retaining authorization checks. Fanout queues can lag during bursts. Duplicate/out-of-order events require versioned idempotent feed insertion. A deleted post may remain referenced in many feeds, so hydration must suppress it even before asynchronous cleanup finishes.

A celebrity post can overload one fanout partition or hot object. A cache outage multiplies hydration reads. Ranking service failure should allow an explicit chronological fallback if product requirements permit. Rebuilding a user's feed needs a bounded history and a way to reconcile follow changes during rebuild.

### Consistency, security, observability, trade-offs — steps 11–14

New posts can appear eventually, but block/private visibility must be enforced at serving time under a defined revocation policy. A user should see their own new post through mutation response/session handling even while fanout catches up. Pagination may trade a stable session snapshot for fresher rankings; document duplicates/omissions if stability is not promised.

Authorize post reads, protect social-graph privacy, rate-limit spam, and design abuse/moderation workflows. Measure publish-to-feed delay, read p99, fanout backlog/skew, cache miss pressure, and privacy-filter removals. Hybrid fanout reduces extreme write amplification but makes read composition more complex. Do not adopt global strong ordering when per-author/version and session feed semantics suffice.

### Exercises

A private author becomes public, posts, then blocks a follower while fanout is delayed. Define what that follower can see at each step and where current authorization is enforced.

## YouTube-style video platform

### Clarify, require, estimate — steps 1–4

Clarify live versus uploaded video, maximum duration, playback regions, resolutions, rights, privacy, and recommendations. Assume uploaded video, resumable ingestion, asynchronous transcoding, adaptive playback, and private/public visibility. Playback startup and rebuffering matter more than metadata API latency alone.

At 100,000 uploads/day averaging 500 MB, originals add about 50 TB/day. Ten million viewers watching twenty minutes/day at an average 2 Mb/s consume roughly 3 PB/day of playback data in decimal units. This rough estimate immediately motivates object storage, CDN delivery, and careful encoding cost; sharding metadata is not the first bandwidth solution.

### APIs, model, architecture — steps 5–7

Create upload sessions, expose processing status, publish metadata only under a valid lifecycle, and authorize playback manifests. Store video identity, owner, source version/checksum, processing jobs, rendition manifest, visibility, and deletion state.

```text
uploader -> object storage -> ingest/scan -> transcode queue -> workers
                                              -> segments/manifests -> CDN
viewer -> metadata/playback authorization -> manifest -> CDN segments
```

Transcode into a bitrate ladder and segmented representations so clients can adapt to available throughput. The manifest describes available segments/renditions. Preserve the original or a defined source-of-truth asset for regeneration. Metadata/control traffic and bulk video delivery are separate paths.

### Bottlenecks, scaling, failures — steps 8–10

Transcoding consumes substantial CPU/GPU time and can be parallelized by job/segment under codec constraints. Admission and scheduling should prevent one massive upload from monopolizing capacity. Prioritize an initial playable rendition before optional higher quality if product policy permits.

Workers can crash after producing only some segments. Publish a manifest generation only when its referenced output is valid; keep partial output isolated and clean it later. Duplicate jobs use deterministic source-version/encoding-policy identities. A viral video stresses edge misses and origin egress; immutable segment URLs and appropriate CDN caching reduce load.

### Consistency, security, observability, trade-offs — steps 11–14

Processing is asynchronous, so expose pending/ready/failed states truthfully. Visibility changes must affect manifest/segment access with a documented signed-URL/cache window. Validate uploads and isolate decoders; private originals should not become public through predictable storage paths. Rights/moderation decisions are separate product workflows with auditable state.

Measure upload-to-playable time, transcode failures, playback startup, rebuffer ratio, rendition switches, CDN hit rate, and origin egress. More renditions improve adaptation but increase compute/storage. Strongly consistent playback metadata does not make network bandwidth reliable. A managed video platform can be preferable until custom control or economics justify the pipeline.

### Exercises

Design a failed high-resolution transcode when the low-resolution version is ready. Specify publication, retry, user messaging, and cleanup without breaking current playback.

## Google Drive-style storage

### Clarify, require, estimate — steps 1–4

Clarify file sizes, directories, offline edits, sharing, version history, sync, and conflict behavior. Assume private files with explicit sharing, resumable uploads, version history, and multi-device sync. A successful save creates a durable version; concurrent offline edits must not silently overwrite one another.

Assume one million active users upload 20 MB/day: about 20 TB/day of new logical bytes before deduplication and versions. Metadata operations can be numerous but small. Large-file retries, retained versions, and downloads determine bandwidth/storage budgets; millions of tiny files stress metadata and listing separately.

### APIs, model, architecture — steps 5–7

Define upload sessions, conditional `commitVersion(fileId, baseVersion, manifest)`, paginated folder listing, sharing changes, and a change-feed cursor. Store stable file IDs separately from names/paths, parent relationships, permissions, version manifests, chunk references, and tombstones.

```text
client sync engine -> metadata/version API -> transactional metadata store
client ===== chunks =====> object storage
metadata change log -> per-user sync feed -> other devices
```

Chunking permits resume and can deduplicate content where safe. Content-defined chunking can preserve reuse after insertions better than fixed boundaries, but adds CPU/complexity. A manifest commits references to verified available chunks; partial uploads remain uncommitted until finalized.

### Bottlenecks, scaling, failures — steps 8–10

Partition metadata by tenant/user or directory ownership with a strategy for very large shared trees. Cross-directory moves need a clear transactional boundary. Change feeds must support catching up after disconnection; retention expiry requires a full rescan/snapshot protocol.

Two offline clients commit from the same base version. Reject/branch the second into an explicit conflict copy or use a format-specific merge; generic binary files cannot be safely merged by timestamp. Chunk upload success followed by failed metadata commit leaves orphans. Garbage collection must respect live manifests, retained versions, in-progress uploads, and concurrent publication, often through epochs or delayed deletion.

### Consistency, security, observability, trade-offs — steps 11–14

Metadata version commits and permission changes need authoritative concurrency checks. Blob availability must precede publication of references. Sharing links are capabilities with scope/lifetime; cross-tenant deduplication can reveal content equality and complicate encryption, so do not assume it is always acceptable.

Measure sync convergence time, conflict frequency, missing-chunk errors, orphan bytes, restore success, and permission propagation. Separate client-side encryption requirements early because they alter deduplication, search, preview, and recovery. Whole-file uploads and one metadata database may be enough initially; chunking earns its complexity for large files and unreliable networks.

### Exercises

Design garbage collection while one client uploads chunks and another deletes the last visible file version. Show why “reference count is zero right now” can be insufficient without publication coordination.

## Uber-style ride dispatch

### Clarify, require, estimate — steps 1–4

Clarify location freshness, service regions, dispatch latency, driver exclusivity, pricing, cancellation, and payment. Assume city-local matching, location updates every few seconds, and one active assignment per driver. Approximate nearby search is acceptable; double assignment is not.

For 100,000 online drivers updating every five seconds, ingest is about 20,000 location updates/s. Ride requests may be far fewer, but matching repeatedly queries nearby candidates. GPS noise, dense city centers, and event bursts create spatial skew. Location retention has major privacy implications.

### APIs, model, architecture — steps 5–7

Define authenticated location updates with sequence/time, ride request with idempotency key, driver offer/accept, and ride-state transitions. Store authoritative ride/assignment state separately from ephemeral location/presence indexes. Use geographic cells or a spatial index to find candidates, then filter by eligibility and estimated travel time.

```text
driver updates -> location ingestion -> regional spatial index
rider request -> dispatch -> candidate search -> conditional reservation
                          -> offer -> accept -> ride authority
```

Start with a transactional assignment authority per region. Atomically transition an available driver into a reserved/assigned state for one ride. A location-cache record saying “available” is only a candidate hint; the authoritative conditional transition decides ownership.

### Bottlenecks, scaling, failures — steps 8–10

Partition by geographic region/cells, but allow boundary searches into neighboring cells. Dense cells may need subdivision; moving drivers cross partitions and can have delayed updates. Reject stale sequence updates and expire old locations. A global partition key by driver distributes updates but makes geographic query fanout costly.

An offer timeout does not prove the driver never accepted. Use offer identities, deadlines interpreted at authority, and versioned state transitions. Old accept messages must not claim a driver after a newer reservation. Ride cancellation and payment are a saga with explicit compensations/unknown outcomes. Network loss mid-ride requires recoverable state, not automatic abandonment.

### Consistency, security, observability, trade-offs — steps 11–14

Nearby search can be eventually consistent, while assignment must enforce exclusivity. Clients display freshness/confidence appropriately; no system can turn stale GPS into exact current position. Authenticate devices/users, restrict location access/retention, detect implausible updates, and protect rider/driver personal data.

Measure location age, match latency, acceptance rate, duplicate-assignment prevention, cancellation transitions, and regional load. More sophisticated optimization can improve matching but adds decision latency and complexity. Begin with a clear invariant and simple regional matching before adding global optimization.

### Exercises

Two dispatchers offer different rides to one driver using stale availability. Show the atomic state transition that permits only one assignment and define what each rider sees.

## Collaborative editor

### Clarify, require, estimate — steps 1–4

Clarify text versus structured documents, offline editing, concurrent participants, undo, comments, and access revocation. Assume rich text, small groups per document, sub-second collaboration, durable history, and optional offline editing. Convergence and intention preservation are distinct goals: replicas can agree on an unpleasant result.

Assume 100,000 concurrent editors producing two operations/s, or 200,000 operations/s before batching. Most documents are quiet; a few shared documents are hot. Operation size, history retention, and snapshot frequency determine storage. Per-document coordination is more relevant than a global operation order.

### APIs, model, architecture — steps 5–7

Use document snapshots plus operation streams with document ID, actor/operation identity, causal/base version, and authenticated permissions. Expose join/snapshot, submit-operation, resume-from-cursor, and history/version endpoints.

```text
editors <-> document session service -> durable operation log
                      |                       |
                      +-> fanout          snapshots/compaction
```

Operational transformation (OT) transforms operations against concurrent changes under an algorithm and control protocol. CRDTs define data/operation merge rules that converge under stated delivery/causality assumptions. Neither means “just sort edits by timestamp.” Rich text, undo, deletion, and cursor positions require careful semantics.

### Bottlenecks, scaling, failures — steps 8–10

Assign active documents to session workers and use an authority protocol for ownership transfer. Batch operations to reduce overhead while respecting interaction latency. Snapshotting bounds join/replay cost; compact metadata only when offline-client and causal-retention assumptions permit it.

Disconnects produce duplicate, delayed, and reordered operations. Stable operation IDs and the selected OT/CRDT protocol handle them; arbitrary last-write-wins document replacement loses edits. A session worker can acknowledge only according to the durability promise. If acknowledgement precedes persistence, a crash can lose accepted edits. Hot documents need fanout/backpressure and may hit inherently sequential coordination limits.

### Consistency, security, observability, trade-offs — steps 11–14

Define local optimistic display, remote convergence, durable save, and conflict/undo behavior separately. Revoked users may retain offline copies, but the server must reject later unauthorized submissions. Sanitize rendered content and constrain operation size/cost so one edit cannot exhaust the session service.

Measure local-to-remote propagation, durable-save delay, replay length, convergence discrepancies, rejected stale/unauthorized operations, and hot-document saturation. A centralized versioned editor can be simpler if simultaneous/offline editing is not required. Use mature OT/CRDT implementations and validate their specific model instead of inventing one from a few examples.

### Exercises

Two offline users insert and delete around the same character. Specify the operation identities and intended merge semantics, then test all delivery orders allowed by the chosen algorithm.

## Payment system

### Clarify, require, estimate — steps 1–4

Clarify whether the system maintains an internal ledger, calls external payment providers, handles refunds, or moves actual funds. Assume an application payment workflow with an auditable internal ledger and external provider integration. Correctness, reconciliation, and access controls dominate raw latency. This is an engineering model; real deployment requirements depend on the payment domain and jurisdiction.

Assume one million payment attempts/day, about 12/s average and 120/s peak, with a much larger read/report workload. This scale does not force sharding. Exact amounts, currencies, immutable operation identities, and durable audit history matter far more than impressive QPS claims.

### APIs, model, architecture — steps 5–7

Define `POST /payment-attempts` with an idempotency key, amount/currency, and authorized business reference; provide status lookup and explicit refund operations. Store payment intent/attempt separately from ledger entries and provider references. Use exact numeric representations and a balanced ledger model appropriate to the domain; corrections append compensating entries rather than silently editing historical amounts.

```text
client -> payment API -> transaction: operation + ledger/state + outbox
                              -> provider worker -> external provider
provider callbacks/reconciliation -> verified state transitions
```

Do not store raw card credentials when a provider tokenization flow can keep that boundary outside the application. Provider credentials and callback verification are narrowly scoped.

### Bottlenecks, scaling, failures — steps 8–10

Enforce unique idempotency scope and fingerprint. Use the same provider operation identity on retries. A timeout after submission is unknown, so query/reconcile before declaring failure or creating a new attempt. The provider may complete after the user closes the page.

Webhook events can duplicate, arrive out of order, or be delayed. Verify signatures and bind them to known operations; use monotonic state transitions or provider event/version semantics. A refund can be pending and fail independently. Outbox/inbox protects local transitions, while provider reconciliation closes cross-system uncertainty. Reconcile ledger/provider totals and investigate differences rather than assuming all callbacks arrive.

### Consistency, security, observability, trade-offs — steps 11–14

Local ledger invariants require transactional enforcement. External settlement is a separate state machine, not a single database commit. Strong local correctness plus eventual external reconciliation is often the honest contract. Least privilege, separation of duties, encrypted transport/storage, secret rotation, and restricted audit access protect different boundaries.

Measure unknown-outcome age, duplicate-suppression conflicts, reconciliation discrepancies, provider error rate, and ledger invariant violations. Avoid putting sensitive payment data in traces. A distributed lock is not a substitute for durable operation identity and provider guarantees. Keep the monetary authority in one transactional boundary until a concrete requirement justifies distributed coordination.

### Exercises

The provider charges successfully, its response is lost, and the callback arrives twice after a retry. Draw every durable state and prove the application neither double-charges nor incorrectly marks the payment failed.

## Distributed task scheduler

### Clarify, require, estimate — steps 1–4

Clarify one-off versus recurring schedules, time zones, missed-run policy, lateness, cancellation, and execution guarantees. Assume millions of schedules, second-level dispatch precision under normal conditions, at-least-once execution attempts, and no silent loss of due runs. “Exactly at 09:00” cannot be guaranteed through arbitrary outages.

Ten million daily schedules average about 116 due runs/s, but a million users choosing the top of the hour creates a large burst. Estimate due-time skew, job duration, and downstream capacity separately. A scheduler can dispatch work faster than workers can safely execute it.

### APIs, model, architecture — steps 5–7

Expose create/update/cancel schedule and list run history. Store schedule definition, time zone, next due instant, version, misfire policy, and stable run identity such as `(scheduleId, scheduledInstant, version)` under the intended recurrence semantics.

```text
schedule API -> schedule store
partition owners -> due-time index/heap -> durable run + outbox -> queue -> workers
```

Start with indexed due-time queries and transactional claiming. At larger scale partition schedules and use per-partition ordered structures or timing-wheel-like buckets. The durable store remains authority; an in-memory timer is a wakeup optimization, not the only record of future work.

### Bottlenecks, scaling, failures — steps 8–10

Owners need leases/epochs and fenced or conditional writes so stale owners cannot create conflicting run state. A unique run identity suppresses duplicate dispatch records. Queue publication follows an outbox so a crash after run creation does not lose execution intent.

Clock jumps, daylight-saving transitions, restarts, and long outages require explicit policy: skip missed runs, catch up every run, or coalesce into one. Compute civil-time recurrences with a time-zone-aware library and define ambiguous/nonexistent local-time behavior. Use monotonic time for local waiting, then recheck authoritative due state. Backpressure prevents catch-up from flooding workers.

### Consistency, security, observability, trade-offs — steps 11–14

Schedule updates/cancellation race with dispatch; a versioned transaction defines the cutover. Cancellation cannot undo an already executed effect. Authenticate schedule ownership, bound frequency and payloads, and isolate tenant quotas. Never execute arbitrary user shell commands in privileged workers without a deliberately sandboxed product model.

Measure dispatch lateness, missed/coalesced runs, duplicate attempts, stale-owner rejections, queue age, and clock anomalies. A single database-backed scheduler may be sufficient for a long time. Distributed ownership adds availability/scale only if its coordination and recovery protocols are correct.

### Exercises

An owner pauses past lease expiry while a new owner dispatches the same due schedule. Show the unique run constraint, fencing/conditional update, and worker idempotency boundaries.

## Large-scale search

### Clarify, require, estimate — steps 1–4

Clarify corpus type, ranking, freshness, languages, filters, permissions, and indexing source. Assume a billion documents, keyword/phrase search, tenant filters, relevance ranking, and minute-level normal update freshness. Search quality and tail latency are both requirements; returning wrong private content quickly is a failure.

At an average 2 KB of source text, raw text is about 2 TB before metadata, postings, positions, replicas, and retained segments. Index size depends heavily on analysis and stored fields. Assume 20,000 queries/s peak with skewed terms; common-term fanout can dominate CPU despite compact requests.

### APIs, model, architecture — steps 5–7

Use a bounded query API with filters, pagination/search-session token, and explicit timeout/partial-result policy. Store document identity, source version, tenant/access fields, analyzed terms/positions, and deletion state. Keep authoritative business data elsewhere if the search index is a rebuildable projection.

```text
source changes -> ingestion/analysis -> sharded inverted indexes + replicas
query -> coordinator -> candidate shards -> top-k results -> merge/rank/hydrate
```

An [inverted index](../11-system-data-structures/inverted-indexes.md) maps terms to postings. Shards return local candidates and scores; the coordinator merges them under ranking/statistics rules. Filter before exposing snippets or document data. A point-in-time/search-after style contract can stabilize deep pagination better than large offsets.

### Bottlenecks, scaling, failures — steps 8–10

Partition documents to balance index size and query load, using routing when tenant-local queries can avoid all-shard fanout. Too many shards increase coordination and memory overhead. Replicas add query capacity and recovery options but also index-update work. Cache common queries carefully with version/filter scope.

One slow shard can dominate a fanout request. Set per-shard budgets and define whether partial results are allowed; hedged requests spend extra capacity and need limits. Segment merges compete with queries for CPU/I/O. Index-generation rebuilds should run beside the live index, validate, catch up, and switch through a controlled alias/pointer. Retained tombstones and source versions prevent stale updates from resurrecting deleted documents.

### Consistency, security, observability, trade-offs — steps 11–14

Search freshness is eventual under the ingestion contract. Current authorization may require an authoritative check or tightly controlled permission projection, especially for revocation. Bound query complexity, expensive regex/fuzzy operations, result sizes, and user-supplied ranking scripts. Restrict raw query logs because they can contain secrets or personal information.

Measure query p99, slow-shard contribution, index lag, merge debt, shard skew, relevance evaluation, and permission-filter correctness. More shards are not automatically more scalable. Start with a managed search engine or database full-text search at smaller scale, and let corpus/query requirements justify distributed search complexity.

### Exercises

A tenant owns 40% of documents and issues 70% of queries. Compare dedicated routing, subsharding, replicas, and query admission while preserving tenant isolation and stable pagination.

## Exercises

Select one design and perform an adversarial review: lose a response after commit, pause an owner, reorder two events, revoke access during a cached read, and restore from a backup. For each, name the invariant, the authority enforcing it, the observable symptom, and the recovery action. Then remove one component and explain exactly which requirement would fail.

<details><summary>Evaluation guide</summary>

Advanced answers preserve explicit guarantees through partial failure. They distinguish authoritative records from projections, local atomicity from external effects, and approximate discovery from exclusive assignment. They include skew, lifecycle cleanup, security, observability, and migration rather than relying on product names as explanations.

</details>

## Further reading and connections

[Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [Spanner paper](https://research.google/pubs/spanner-googles-globally-distributed-database/), [Automerge documentation](https://automerge.org/docs/), [Stripe idempotency](https://docs.stripe.com/api/idempotent_requests), and [Elasticsearch architecture documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/scalability.html). Review [leases/fencing](../10-distributed-systems/leases-and-fencing.md), [outbox/sagas](../20-production-patterns/outbox-inbox-and-sagas.md), [logical time](../10-distributed-systems/logical-time.md), and [observability](../14-observability/logs-metrics-traces.md). Finish with [Relay's evolution](../21-case-studies/relay-evolution.md) and the [mock interviews](../22-interview-preparation/mock-interviews.md).
