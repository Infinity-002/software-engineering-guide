# Replication, quorums, and failover

Copies improve durability and availability only if the system defines how they agree, how a replacement becomes authoritative, and how stale copies are repaired. Replication is a protocol around copies, not the act of storing three files.

## Three replication shapes

Leader/follower replication routes writes through one leader and copies its ordered changes. It simplifies conflict ordering but creates failover and read-lag decisions. Multi-leader replication accepts writes at several leaders, useful for some geographically distributed or offline workflows, but concurrent changes need explicit conflict resolution. Leaderless systems send operations to several replicas and combine responses, often with version metadata and repair.

Last-write-wins using wall-clock timestamps is easy to state but can discard a logically later update when clocks skew. A merge function must reflect domain meaning: adding two shopping-cart items can sometimes merge; assigning two different owners to one exclusive resource cannot be resolved merely by taking a set union.

## Quorum arithmetic gives intersection, not a whole protocol

Let `N` be the number of replicas in the relevant replica set, `W` the number of acknowledgements required for a write, and `R` the number of replicas consulted for a read. If `R + W > N`, every such read set intersects every such write set. If `W > N/2`, two write quorums intersect.

For `N=3`, `W=2`, `R=2`, a read of B/C intersects a write acknowledged by A/B at B. But the reader still needs to identify the correct version and handle concurrent/incomplete writes. Intersection alone does not establish linearizability. Sloppy quorums that temporarily use different replica sets, conflict resolution, failed partial writes, membership changes, and stale versions complicate the argument.

```text
replicas: A B C
write:    A B      (acknowledged)
read:       B C    (intersects at B)
```

Ask what an acknowledgement means: received in memory, durable on storage, replicated, or applied and readable. `W=2` with volatile acknowledgements does not prove survival of two power losses. A read from an intersecting node may still need a version-selection and write-back protocol to safely expose the right value.

## Repair is part of convergence

Read repair uses observed differences during a read to update stale replicas. Anti-entropy compares replicas periodically, often with [Merkle trees](../11-system-data-structures/merkle-trees.md), to find divergence without transferring everything. Hinted handoff can retain work for an unavailable replica and deliver it later under the system's rules.

Deletes need tombstones or equivalent versioned deletion information. Removing the only evidence of a delete too early can let an old replica reintroduce the value. Retention must account for maximum supported offline time and repair guarantees. “Eventually consistent” requires these mechanisms and assumptions; it is not a force of nature.

## Failover transfers authority

A leader stops responding. Followers cannot know whether it crashed or merely lost contact. Promoting a replacement while the old leader can still write creates split brain. A safe protocol uses terms/epochs, quorum decisions, and enforcement that obsolete authority cannot commit conflicting work.

In asynchronous replication, the replacement may lack recently acknowledged writes. The system must state its loss/failover policy. Synchronous replication reduces certain loss windows but can block when required replicas are unavailable. Serving follower reads introduces freshness decisions independent of write durability.

A client may cache the old leader address. It needs redirection/discovery and retry semantics, but an old endpoint accepting a write must not defeat the authority protocol. Fencing belongs where the effect is accepted, not just in the caller's belief.

## Membership changes are unusually subtle

If one group believes the voters are A/B/C and another believes D/E/F, each can assemble its own “majority.” Safe reconfiguration requires overlap or a protocol such as joint consensus, not just replacing a configuration file on each machine. Adding replicas can temporarily increase bandwidth and recovery load; redundancy is not cost-free during the operation meant to improve safety.

Why not let every replica accept all writes? That can be valid when conflicts have acceptable merge semantics. It is unsafe for invariants requiring one decision unless another coordination mechanism enforces them. Why not read every replica every time? It increases latency and failure dependence while still requiring a correct version protocol.

## Exercises

1. **Check:** For `N=5`, compare `(W=3,R=3)` and `(W=1,R=1)`. What does each arithmetic result prove and not prove?
2. **Predict:** A deleted record returns after an offline replica rejoins. Explain the missing retention/repair assumption.
3. **Design:** Specify failover behavior for Relay task edits with a five-second replica lag.
4. **Interview:** Give a counterargument to “R + W > N guarantees strong consistency.”

<details><summary>Hints</summary>

Intersection is a set property; ordering, version choice, durability, and membership are protocol properties. Incomplete writes can leave versions on some nodes. Tombstone garbage collection must respect repair and offline-replica assumptions.

</details>

## Further reading and connections

[Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [Cassandra consistency](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html), and [Raft paper](https://raft.github.io/raft.pdf). Continue to [consensus](consensus-and-leadership.md), [logical time](logical-time.md), and [database scaling](../06-databases/scaling-and-nosql.md).
