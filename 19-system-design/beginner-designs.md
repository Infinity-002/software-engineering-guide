# Four foundational designs

Each walkthrough follows the [fourteen-step method](methodology.md), grouping related decisions so the reasoning remains readable. Numbers are explicit exercise assumptions, not facts about a commercial service. Start each design without looking at its proposed architecture, then compare your invariant and failure analysis.

## URL shortener

### Requirements and scale — steps 1–4

Clarify whether links are public, editable, expiring, or private, and whether click analytics must be exact. Assume public redirects, authenticated creation, optional expiry, and approximate analytics. Redirect latency matters more than creation latency; newly created links should work immediately. Abuse and takedown are core requirements because the system can redirect people to hostile content.

Assume one million creations/day and 100 million redirects/day: roughly 12 writes/s and 1,160 reads/s average, with a tenfold redirect peak. At 500 bytes of logical metadata per link, creation adds about 500 MB/day before indexes and replicas. A small relational service is a plausible initial authority; redirects dominate scaling.

### APIs, data, and initial architecture — steps 5–7

Use `POST /links` with a destination, expiry, and optional idempotency key; return a short code. `GET /{code}` resolves it and returns an appropriate redirect. Store `code` as a unique key with destination, owner, creation/expiry, and disabled state. Treat user-provided URLs as data and allow only intended schemes.

```text
client -> redirect API -> indexed link table
creator -> authenticated API -> same authority
```

Generate sufficiently large random codes and retry on a unique-key conflict, or allocate IDs and encode them with a policy addressing enumeration. For random space `M` and `n` generated values, collision probability grows approximately with `n²/(2M)` while small; uniqueness enforcement is still required. Do not claim random IDs can never collide.

### Bottlenecks, evolution, and failures — steps 8–10

Add a cache for popular immutable mappings when database read load warrants it. Edge caching can reduce latency further, but edit/takedown/expiry policy must reach cached redirects. A viral link becomes a hot key; short local caching and CDN reuse help more than sharding that one key. Emit click analytics asynchronously so a slow analytics pipeline does not block redirects.

A cache outage needs origin admission limits. A creation response lost after commit should replay through its key. If the authority is unavailable, cached active mappings may remain serviceable under a defined stale policy; unknown mappings should not be invented. Background expiry cleanup does not replace checking expiry on reads.

### Consistency, security, observability, trade-offs — steps 11–14

Read-your-writes can route initial resolution to authority or populate cache only after commit. Takedown freshness may need a stronger invalidation/revocation path than ordinary destination updates. Authenticate management operations, prevent unauthorized ownership changes, rate-limit creation, and isolate any URL-scanning fetcher against SSRF.

Measure redirect latency/error rate, cache hit/fill behavior, disabled-link propagation, collision retries, and analytics lag. Avoid storing unnecessary personal click data. Permanent redirects can be cached aggressively by clients, making later changes harder; temporary redirects preserve flexibility at a different caching cost. Do not shard before measuring the indexed workload.

### Exercises

Design a link that must be disabled worldwide within 30 seconds. Which caches and client behaviors challenge that promise? Calculate code-space collision risk for your chosen length, then show how the database handles an actual collision.

## Pastebin

### Requirements and scale — steps 1–4

Clarify maximum paste size, syntax highlighting, edit history, privacy, expiry, and search. Assume immutable text pastes up to 1 MB, optional authenticated ownership, unlisted/public modes, and expiry. “Unlisted” means hard to discover, not authenticated secrecy. Require safe display of arbitrary text and durable content after acknowledged creation.

Assume 100,000 pastes/day averaging 20 KB: about 2 GB/day of raw text. Ten reads per paste gives one million reads/day, modest average QPS but potentially highly skewed. Storage retention and abusive content dominate before raw request throughput.

### APIs, data, and initial architecture — steps 5–7

`POST /pastes` accepts bounded text and visibility/expiry; `GET /pastes/{id}` returns authorized content/metadata. Store identity, owner, visibility, expiry, content hash, and either text or an object key. Start with PostgreSQL for bounded small content if operational simplicity wins; move larger bodies to object storage when backup/serving cost warrants it.

```text
browser -> API -> metadata database
             -> text body or private object store
```

Render paste text as text, not executable HTML. Syntax highlighting must preserve that boundary. A content hash can check integrity, but using it as a global public identifier can reveal content equality and facilitate guessing of low-entropy private text.

### Bottlenecks, evolution, and failures — steps 8–10

Popular public pastes can be cached at the edge. Private pastes need authorization-aware serving and cache policy. If content and metadata are stored separately, model pending/ready state and reconcile orphan objects or missing uploads. An expired paste must stop being served before eventual physical deletion finishes.

Limit request size before buffering, bound decompression, and rate-limit creation/download abuse. A viral large paste can saturate egress even with low API CPU. Retention jobs should delete in batches and preserve a recoverable audit of lifecycle decisions where required.

### Consistency, security, observability, trade-offs — steps 11–14

Publish the paste only after its content is durably available under the storage contract. Define whether expiry is strict at every edge or subject to a bounded cache window. Access checks must apply to raw-download endpoints as well as the HTML page. Use safe content types and disposition, CSP, and an isolated origin for any risky rendering behavior.

Measure upload success, ready-state delay, missing-object errors, expiry violations, egress, and cleanup backlog. Encryption at rest protects storage media under its key model, not against authorized application reads. Avoid a full search engine unless public search is actually required. Immutable content simplifies caching; editable pastes need versions and more invalidation machinery.

### Exercises

Design “private paste shared with three users” separately from “unlisted paste.” Inject a crash after object upload but before metadata commit and specify cleanup without deleting another user's object.

## Rate limiter service

### Requirements and scale — steps 1–4

Clarify whether this protects capacity, enforces paid quotas, or both. Assume abuse protection for 50,000 checks/s, per-tenant and route limits, bounded bursts, and low added latency. Permit a documented small overshoot during failover; exact paid accounting remains in a transactional authority. This distinction determines whether Redis-backed approximate state is acceptable.

Estimate active keys and state size, not only checks/s. One million active identities with 100 bytes of logical state is 100 MB before allocator/key/replication overhead. Arbitrary attacker-selected identities can make state cardinality unbounded without admission/expiry.

### APIs, data, and initial architecture — steps 5–7

Expose an internal `CheckAndConsume(identity, policy, cost)` operation returning allowed/remaining/retry guidance. Authenticate callers so they cannot impersonate other tenants or choose cheaper costs. Store bucket state keyed by policy and principal, with a stable policy version and bounded lifetime.

```text
edge/API -> limiter -> atomic Redis bucket operation
                  -> cached policy configuration
```

Use a token bucket for explicit burst capacity and sustained rate. Refill, decision, and deduction must be atomic. The [rate-limiting chapter](../13-reliability/rate-limiting.md) explains algorithms and race conditions.

### Bottlenecks, evolution, and failures — steps 8–10

A central limiter adds a network hop and can become hot. Shard independent keys, isolate global policies, or lease small token batches to local instances when bounded overshoot is acceptable. A globally shared bucket remains a coordination hotspot; splitting it changes the guarantee.

If the limiter is unavailable, apply a per-route fail-open/fail-closed policy plus a local emergency bound. Do not accidentally grant infinite capacity. Redis failover may lose recent deductions under asynchronous replication. Clock jumps can refill too much unless the algorithm/time model handles them. Policy updates must avoid resetting every bucket into a synchronized full burst without intent.

### Consistency, security, observability, trade-offs — steps 11–14

Specify the maximum overshoot from local batches and failure recovery. Exact quota requires durable accounting and idempotent charging, not simply a more complicated token bucket. Verify forwarded client identity only from trusted edges, protect policy administration, and consider shared NAT fairness.

Measure decision latency, allow/deny rate by bounded policy labels, state cardinality, backend errors, and local fallback activation. Test fairness under a noisy tenant, not only uniform load. Choose a library/local limiter for a single instance; add a service only when shared budget and governance justify it.

### Exercises

Derive a worst-case overshoot bound when each of 20 API instances holds up to 50 leased tokens. Explain what happens when a policy is tightened while those tokens remain outstanding.

## File upload service

### Requirements and scale — steps 1–4

Clarify maximum size, resumability, privacy, malware scanning, transformations, and deletion. Assume private workspace attachments up to 2 GB, resumable upload, and no public visibility before validation. The API must remain responsive while bulk bytes flow elsewhere.

At 100,000 uploads/day averaging 10 MB, original storage grows about 1 TB/day. If each is downloaded three times, egress can exceed 3 TB/day before retries and variants. Bandwidth and retention drive the design more than metadata QPS.

### APIs, data, and initial architecture — steps 5–7

`POST /upload-intents` checks quota and creates a scoped object key. Return constrained upload capability/part instructions. `POST /upload-intents/{id}/complete` requests verification, and `GET /attachments/{id}` exposes status or an authorized download capability. Store tenant, owner, expected limits, object identity/version, checksum, lifecycle state, and expiry.

```text
browser -> API -> intent database
browser ===== bulk bytes =====> object storage/quarantine
completion -> verification/scan queue -> worker -> ready metadata
```

### Bottlenecks, evolution, and failures — steps 8–10

Direct uploads keep API memory and bandwidth bounded. Multipart/resumable storage operations limit restart cost for large files. Workers scale by CPU and provider limits; scanning backlog should leave files quarantined, not bypass validation. Clean abandoned multipart uploads and expired intents.

Completion may duplicate, arrive before storage is fully ready, or never arrive. Verify the server-created object identity and actual metadata; make transitions idempotent. A successful upload followed by database failure creates an orphan requiring reconciliation. A completed scan for an older object version must not mark a replaced object safe.

### Consistency, security, observability, trade-offs — steps 11–14

Only publish a specific verified object version after required checks. Reauthorize downloads and define revocation behavior for already-issued signed URLs. Validate content, size, expansion, filenames, and parser resource usage. Isolate untrusted content from the application's script origin.

Measure upload completion, quarantine age, scan failures, orphan bytes, download latency, and storage/egress cost. A proxy upload is simpler for small files and centralized controls; direct upload scales bulk traffic but adds capability and lifecycle complexity. Do not promise immediate deletion from every backup/cache without a retention model.

### Exercises

Design a version-bound scanning result and a reconciliation job. Show how a user closing the tab, an expired signed URL, and a duplicated completion callback each reach a safe terminal state.

## Exercises

Choose one design and write all fourteen decisions without the chapter. Change one requirement—strict revocation, tenfold peak, private sharing, or regional outage—and identify exactly which assumptions break. Implement one failure experiment rather than only drawing the happy path.

<details><summary>Cross-design review rubric</summary>

Check authoritative identity, uniqueness, bounded resources, cache scope, retry semantics, lifecycle cleanup, and observability. Strong answers explain why an omitted component is unnecessary at the stated scale and identify a measurable trigger for adding it.

</details>

## Further reading and connections

[HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110), [S3 multipart overview](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html), and [OWASP file upload guidance](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html). Review [cache design](../07-caching/cache-design.md), [idempotency](../20-production-patterns/idempotency-and-deduplication.md), and [upload flows](../12-fullstack/realtime-and-uploads.md) before [intermediate designs](intermediate-designs.md).
