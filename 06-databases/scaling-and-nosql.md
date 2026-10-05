# Replication, partitioning, and data models

Relay's database becomes busy. The first question is which resource and workload dominate: reads, writes, storage, lock contention, or inefficient queries? Different scaling mechanisms move different limits and introduce different correctness problems.

## Replicas copy; partitions divide

A read replica can serve queries while a leader handles writes. Asynchronous replication allows acknowledgement before the replica catches up, reducing write latency but exposing lag and possible data loss during failover. Synchronous replication waits for a configured remote acknowledgement condition. That condition might mean received, persisted, or applied depending on the system; name it precisely.

A user creates a task on the leader, then reads a lagging replica and sees no task. Options include routing the session's reads to the leader temporarily, waiting for a known replication position, or presenting a UI that tolerates pending visibility. A fixed delay is a heuristic, not proof of catch-up. Replica lag also affects authorization changes: stale permission data may be a security issue rather than a cosmetic delay.

Partitioning divides a dataset into pieces, sometimes within one database instance. Sharding distributes ownership across independent storage nodes or groups. Replicas improve redundancy/read capacity; shards divide data/write load. You can use both, but neither eliminates cross-partition coordination costs.

## Choose the partition key from access patterns

Hashing `workspace_id` keeps a workspace's tasks together and spreads many workspaces. One enormous workspace can still become a hot partition. Time-range partitioning supports retention and range queries but directs current writes toward the newest range. A uniformly distributed key may spread writes while making range queries fan out.

```text
tenant directory -> shard ownership
workspace A -> shard 1 -> replicas
workspace B -> shard 2 -> replicas
workspace C -> shard 1 -> replicas
```

Resharding requires moving data while reads and writes continue. Define a migration state, route authority, copy/catch-up process, cutover condition, and fallback. Dual writes without a protocol can diverge. Use versioned routing/epochs and reconciliation; callers must handle stale placement information. [Consistent hashing](../11-system-data-structures/consistent-hashing.md) reduces placement movement but is not a complete migration protocol.

Global uniqueness, foreign keys, joins, and transactions become harder across shards. Sometimes a central allocator or globally unique ID is appropriate; sometimes uniqueness only needs to hold within a tenant. Clarifying that requirement can avoid a distributed transaction entirely.

## Data models optimize different operations

| Family | Natural strength | Cost or missing assumption to examine |
|---|---|---|
| Key-value | Direct lookup by key | Secondary querying and multi-key invariants |
| Document | Aggregate-shaped nested records | Duplication and cross-document coordination |
| Wide-column | Partition-key access and ordered clustering within partitions | Hot partitions and query-driven modeling |
| Graph | Traversal of relationships | Partitioned traversal cost and workload fit |
| Search engine | Text relevance, filtering, inverted indexes | Refresh lag and source-of-truth semantics |
| Relational | Joins, constraints, flexible structured queries | Distribution and workload-specific tuning |

These categories overlap. SQL databases can store JSON and perform full-text search; document databases can support transactions; distributed SQL can coordinate strongly consistent operations at a cost. Ask about the exact product and configuration, not a slogan about SQL versus NoSQL.

A search index for Relay can be an asynchronous projection of PostgreSQL. That makes search results briefly stale. Recheck authorization and current existence when opening a result, and propagate deletions/revocations promptly. Rebuilding the index from authoritative data is an essential repair capability.

## Scaling decisions and failure scenarios

Before sharding, fix poor queries, missing indexes, connection storms, avoidable reads, and oversized transactions. Vertical scaling, read replicas, caching, and archiving may be sufficient. Sharding too early adds routing and migration complexity to every feature.

Failover can lose acknowledged writes if the durability contract allowed them to exist only on the failed leader. Promoting a stale replica without fencing the old leader can create conflicting writers. A replica can be healthy as a process but too far behind to serve a freshness-sensitive read. Monitor apply lag, replication positions, and workload impact rather than relying on one “replica up” flag.

## Exercises

1. **Design:** Choose a partition key for tenants ranging from 10 to 10 million tasks. Explain the escape hatch for the largest tenant.
2. **Predict:** An asynchronous replica is promoted after a leader crash. Which acknowledged writes might disappear?
3. **Debug:** Search shows a deleted private task. Separate index lag, authorization enforcement, and deletion propagation.
4. **Interview:** Explain why adding replicas does not automatically increase write throughput.

<details><summary>Hints</summary>

Replicas must still apply the write stream. Large tenants may need subpartitioning or dedicated placement. Promotion safety requires both a durable-history policy and prevention of obsolete authority continuing to write.

</details>

## Further reading and connections

[PostgreSQL high availability](https://www.postgresql.org/docs/current/high-availability.html), [Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), and [Elasticsearch near real-time search](https://www.elastic.co/guide/en/elasticsearch/reference/current/near-real-time.html). Continue to [quorums](../10-distributed-systems/replication-and-quorums.md), [caches](../07-caching/cache-design.md), and [search indexes](../11-system-data-structures/inverted-indexes.md).
