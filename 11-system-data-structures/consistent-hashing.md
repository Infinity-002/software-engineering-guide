# Consistent hashing and placement

Relay distributes cache keys across four servers using `hash(key) % 4`. Adding a fifth server changes the modulus, remapping many keys even though most servers remain. The resulting cold-cache wave can overload the database. Consistent hashing reduces movement when membership changes.

## Place both keys and servers in a hash space

Imagine hash values arranged on a circle. Each server owns positions on that circle. A key is assigned to the first server position clockwise from the key's hash. Adding a position changes ownership only for the interval immediately preceding it; removing one transfers its interval to the next position.

```text
clockwise hash space: 0 ---- A ---- key x ---- B ---- C ---- wrap
owner(x) = B
insert D between x and B -> x moves to D
keys in unrelated intervals stay put
```

With balanced random placement, adding one server to `n` servers moves roughly `1/(n+1)` of the keys in expectation. This is a distribution assumption, not a guarantee that exactly that fraction of traffic or bytes moves. One key can account for most requests.

## Virtual nodes improve balance and weighting

One random position per physical server can create uneven intervals. Give each server many virtual positions and aggregate their ownership. This smooths random imbalance and allows larger machines to receive more positions. More virtual nodes increase routing metadata and movement bookkeeping, so there is a practical trade-off.

Uniform key count does not imply uniform load. Large objects, expensive requests, and a hot tenant can dominate. Monitor bytes, CPU, and request rate per owner. For a single hot cache key, replicating reads or local caching may matter more than placement.

## Placement is not migration or consistency

Every client needs compatible membership and hashing configuration. During a membership update, old clients may send a key to the old owner while new clients use the new owner. For a disposable cache, misses and temporary duplication may be acceptable. For authoritative storage, define handoff, forwarding, versioning, copying, catch-up, and cutover.

Replication often places copies on several successors, but naive virtual-node successors can belong to the same physical host or failure domain. Choose distinct hosts/zones according to the durability policy. A ring diagram without failure-domain awareness can look redundant while losing all copies in one rack failure.

If a server fails, its intervals move to neighbors and its traffic concentrates there. Capacity planning must include this failover load. Fast failure detection can also create churn during transient network problems; placement authority and membership epochs must avoid contradictory ownership where correctness requires it.

## Alternative placement models

Rendezvous hashing scores each candidate server for a key and chooses the highest score, offering stable movement with a different lookup/metadata trade-off. A directory can map tenants to shards explicitly, making exceptions and large-tenant moves easier. Fixed logical partitions decouple key placement from physical servers: keys map to partitions, and a control plane moves partitions between machines.

Why not always use a ring? Small static deployments may be fine with modulo hashing. Tenant-specific placement and residency constraints may be clearer with a directory. Range partitioning supports ordered scans that hash placement scatters. Choose based on movement, query locality, skew, and operational control.

## Exercises

1. **Implementation:** Hash 100,000 synthetic keys with modulo and a virtual-node ring. Add a server and compare movement and distribution.
2. **Predict:** A server owns 10% of keys but receives 80% of requests. Why did balanced hashing fail to balance work?
3. **Design:** Place three replicas across zones and explain how virtual nodes avoid selecting the same host twice.
4. **Debug:** Two clients use different ring versions during a write. Specify the safe behavior for a cache and for an authoritative store.
5. **Interview:** Explain why consistent hashing does not by itself solve resharding.

<details><summary>Hints</summary>

Placement chooses destinations; migration preserves data and authority while destinations change. Compare key count, byte size, and request cost separately. A membership version can help detect stale routing, but the receiving system still needs a handoff policy.

</details>

## Further reading and connections

[Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [Cassandra architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html), and [Envoy load balancing](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers). Connect to [sharding](../06-databases/scaling-and-nosql.md), [cache outages](../07-caching/cache-failures.md), and [quorums](../10-distributed-systems/replication-and-quorums.md).
