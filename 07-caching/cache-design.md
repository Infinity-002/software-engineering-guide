# Designing caches and freshness contracts

Relay repeatedly reads the same task summary from PostgreSQL. A cache can avoid repeated work and shorten the network path. The benefit comes from locality: recently or frequently used values are likely to be useful again. The cost is that a copied value can outlive the fact that produced it.

## Name authority, key, lifetime, and failure policy

Before adding Redis, answer four questions. Which system owns the truth? What exactly identifies a representation? How stale may it be? What happens when the cache is unavailable? A cache is a performance mechanism only if correctness remains defined on misses, eviction, and restart.

Browser HTTP caches, CDNs, in-process caches, shared Redis caches, and database buffer pools all reuse work at different boundaries. A database buffer pool retains pages under the database's concurrency rules; a JSON cache outside the database does not inherit those rules. A client query cache stores a representation of remote state and has its own identity and lifecycle.

## Read and write strategies

| Strategy | Mechanism | Main consequence |
|---|---|---|
| Cache-aside | Application reads cache, fills from authority on miss | Simple, but application owns races and invalidation |
| Read-through | Cache abstraction loads misses | Centralizes loading, still needs freshness semantics |
| Write-through | Write path synchronously updates cache and backing store under its contract | Extra latency; two failures need coordination |
| Write-behind | Cache accepts a write and persists later | Fast acceptance but possible loss/reordering before persistence |

“Write-through” does not magically create an atomic transaction across Redis and PostgreSQL. State which write wins, when acknowledgement happens, and how partial success is repaired. If Redis is authoritative, you are designing a datastore with persistence/replication guarantees, not merely adding a disposable cache.

TTL bounds ordinary residence time after insertion, not necessarily staleness since the source changed. A delayed loader can insert already-old data with a new TTL. Eviction frees capacity; LRU favors recently used entries, LFU favors frequently used entries, and real implementations may approximate both. Memory pressure can evict a key before TTL. Do not use cache presence as proof that a durable business fact exists.

## The invalidation race

```text
reader A misses cache and reads database version 7
writer B commits database version 8
writer B deletes cache key
reader A stores version 7 into cache
```

“Update database, then delete cache” is often useful but does not eliminate this stale-fill race. Options include versioned keys/values with conditional installation, generation counters, ordered invalidation streams, shorter tolerated TTLs, or reading sensitive data directly from authority. Each option needs a clear synchronization point. Delayed double deletion can reduce probability but is not a universal proof of freshness.

Never invalidate before committing the database change and assume the problem is solved: a reader can repopulate the old value before the commit. For strict invariants such as available funds or permission revocation, treating a weakly coherent cache as authority can be unacceptable.

## Keys are correctness boundaries

`task:42` may be insufficient if IDs are tenant-local or representations depend on permissions, locale, or schema version. A key might include workspace and representation version. Cache only the fields safe for every caller sharing the key, or separate raw entity caching from caller-specific authorization and shaping.

The famous cache-invalidation-and-naming joke points to the same issue: a name must identify precisely which fact was cached, and invalidation must find every representation affected by a change. Naming and freshness cannot be designed independently. Maintain a small representation graph: changing a task can affect its detail, workspace list, counts, search projection, and activity feed.

## Production trade-offs

A cache with a 99% hit rate can still generate a destructive miss burst. Measure origin request rate, hit/miss latency, fill duration, eviction rate, memory, key distribution, and stale-value incidents. Cache hit rate alone does not measure correctness or user experience.

Why not cache everything? Low-reuse data consumes memory without saving much work; sensitive data creates retention risks; frequently changing data creates invalidation cost. Why not store everything in Redis? It may be a valid datastore for some workloads, but persistence, memory cost, access patterns, failover loss, and durability must be deliberately selected. A relational authority with a disposable cache often has a simpler recovery story.

## Exercises

1. **Predict:** Explain why a 60-second TTL does not always guarantee data is at most 60 seconds old.
2. **Debug:** Reproduce the stale-fill timeline and propose a version-aware repair.
3. **Design:** Choose freshness policies for public avatars, task titles, workspace membership, and payment balance.
4. **Implementation:** Add cache-aside reads, record hits/misses/fill time, and demonstrate correct behavior with Redis unavailable.
5. **Interview:** Explain stale account information using at least three different cache layers.

<details><summary>Hints</summary>

A loader may read stale replica data or pause before storing. Permission changes may require authoritative checks or strongly enforced versioning. Cache failure fallback needs admission limits so the database is not flooded.

</details>

## Further reading and connections

[Redis eviction](https://redis.io/docs/latest/develop/reference/eviction/), [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111), and [AWS caching challenges](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/). Continue to [stampedes](cache-failures.md), [server state](../04-frontend/state-and-data-fetching.md), and [replication lag](../06-databases/scaling-and-nosql.md).
