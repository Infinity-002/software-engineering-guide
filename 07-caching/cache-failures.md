# Stampedes, hot keys, and cache outages

At noon, Relay's most popular workspace summary expires. One hundred thousand requests miss together. Each asks PostgreSQL to rebuild the same value, turning a healthy cache into a synchronized overload trigger. This is a cache stampede: duplicated regeneration work during a miss interval.

## Collapse work, then bound what remains

Single-flight/request coalescing lets one caller perform a fill while others await the result. Within one process, a map of key to in-flight promise can implement the idea. Remove failed/completed entries in a cleanup path, bound the map, and propagate errors intentionally. Across many API processes, local coalescing still permits one fill per process; that may be acceptable and simpler than global coordination.

```text
1000 local misses -> one fill promise -> one database query
                      |
                 shared result
```

A distributed fill lease can reduce duplicate work further, but [lease safety](../10-distributed-systems/leases-and-fencing.md) matters if the work has side effects. For regenerating a disposable cache value, occasional duplicate computation may be harmless; choose the simplest acceptable guarantee. Do not hold all waiting requests indefinitely if the filler crashes.

Stale-while-revalidate serves an explicitly tolerated old value while a refresh occurs. Define a fresh interval, a stale-but-servable interval, and a hard expiry. It is useful for public summaries, dangerous for revoked access or current balances. A stale response should not silently bypass a stronger product promise.

## Similar failures have different shapes

**Cache penetration** means repeated lookups for nonexistent values reach the origin because nothing is cached. Short negative caching can help, but must be scoped and invalidated when a value is created. A [Bloom filter](../11-system-data-structures/bloom-filters.md) can reject definitely absent keys when it contains all relevant inserted keys; a stale filter must not incorrectly suppress newly created data.

**Cache avalanche** is broad simultaneous expiry or cache loss across many keys. Add TTL jitter to avoid synchronized expiration, warm selected high-value keys, and limit origin concurrency. Jitter spreads load; it does not create extra database capacity.

A **hot key** concentrates traffic on one cache shard. Adding shards may not help that one key. Replicate read-only hot values locally, use short-lived per-process caching, partition an aggregatable value, or redesign the access pattern. Consistency and invalidation become more complex as copies multiply.

## Redis failure can move the bottleneck instantly

A service at 50,000 reads/s with 99% cache hits sends about 500 reads/s to its database in steady state. Losing the cache can raise origin demand toward 50,000/s, a hundredfold change. “Fall back to the database” is incomplete unless the database can handle that load or admission control bounds it.

Use a concurrency budget for origin fills, prioritize critical operations, shed optional work, and serve safe stale content where allowed. A circuit breaker can stop repeated slow cache connection attempts, but then the origin budget is even more important. Monitor cache timeouts separately from true misses; otherwise an outage looks like a normal hit-rate fluctuation.

## Recovery is another surge

When Redis returns, all clients may reconnect and refill. Apply reconnect backoff/jitter, controlled warming, and bounded background refresh. Loading every possible key at once can reproduce the outage against the database. Warm by observed value and cost, not merely by table order.

The cache's memory policy also matters. A workload with many one-off large objects can evict frequently reused small objects. Bound object sizes and consider workload separation only when evidence shows interference. Separate pools can isolate risk but increase operational and capacity-management cost.

## Why not lock every miss?

Coordination adds latency, an authority dependency, and failure cases. For cheap fills, duplicate work may cost less than a distributed lock. For expensive fills, local coalescing plus a global concurrency limit may be enough. The objective is bounded origin work and acceptable freshness, not perfect elimination of every duplicate computation.

## Exercises

1. **Predict:** A cache outage changes a 99% hit workload to all misses. Estimate origin amplification and identify the first admission boundary.
2. **Implementation:** Implement local single-flight with bounded waiting and error cleanup; inject a failing fill and prove later requests can retry.
3. **Design:** Handle 100,000 simultaneous misses for a public dashboard and for an authorization record. Explain why the policies differ.
4. **Interview:** Distinguish penetration, stampede, avalanche, and a hot key using symptoms and measurements.

<details><summary>Hints</summary>

Protect the origin before a queue becomes unbounded. Public summaries may tolerate stale values; permission decisions may require an authoritative path or safe denial. Expiry jitter solves synchronized time, not skewed key popularity.

</details>

## Further reading and connections

[AWS caching challenges](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/), [Redis latency diagnosis](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/), and [RFC 5861 stale controls](https://www.rfc-editor.org/rfc/rfc5861). Connect to [load shedding](../13-reliability/resilience-and-recovery.md) and [consistent hashing](../11-system-data-structures/consistent-hashing.md).
