# Leases, distributed locks, and fencing tokens

Relay has a worker that creates one daily billing export. Two workers should not simultaneously publish conflicting versions. A local mutex protects threads in one process; it cannot coordinate independent machines. A permanent distributed lock seems to solve the problem until its holder crashes and never releases it.

## Expiration trades indefinite blockage for a new safety problem

A lease grants temporary authority over a resource. A **lease authority** records who holds it and under what expiration rules. The holder acquires the lease, periodically renews it while working, and releases it when finished. If the holder crashes, expiration eventually allows another holder to proceed.

The authority might be a consensus-backed coordination service, a database transaction with a time-based record, or another service with an explicit consistency model. Its own failover and storage behavior matter. If two authorities can independently grant conflicting leases during a partition, expiration alone does not establish exclusive ownership.

```text
authority: resource export-2026-10-04
  holder = worker A
  lease identity = random ownership token
  epoch = 41
  expiry = authority-defined deadline
```

The random ownership token identifies this acquisition and prevents an old client from deleting somebody else's lock. The increasing epoch is a potential fencing token. These are different jobs; uniqueness does not imply order.

## The stale-holder timeline

Suppose A acquires a ten-second lease. After two seconds it pauses for a long garbage collection or loses CPU scheduling. The authority expires A's lease at ten seconds. B acquires a new lease and starts working. A resumes at fifteen seconds and continues from the instruction after its last ownership check.

```text
time   A                         authority               B
0      acquire ----------------> grants epoch 41
2      pauses
10                               expires 41
11                               grants epoch 42 <------ acquire
12                                                        writes result
15     resumes, writes old result
```

At no point did the authority intentionally grant overlapping valid leases. Yet both processes executed work. Expiration changes authority state; it does not stop a paused machine, cancel a packet already in flight, or erase a stale holder's memory.

Checking “do I still own the lock?” immediately before a write is insufficient: a pause can occur after the check and before the write. The correctness decision must reach the resource that accepts the effect.

## Fencing makes stale authority rejectable

Each acquisition receives a monotonically increasing fencing token from a trustworthy authority. The protected storage service remembers the highest accepted token for the resource and atomically rejects operations with lower tokens. After B's token 42 is accepted, A's token 41 cannot overwrite B's work.

```text
storage operation (pseudocode, atomic at the resource)
  if request.fence < resource.highestFence:
      reject stale owner
  resource.highestFence = request.fence
  apply request under the resource's normal concurrency rules
```

If several operations from the same acquisition legitimately share a token, accepting equal tokens requires an additional ordering/idempotency policy for those operations. If exactly one effect per epoch is allowed, the conditional rule can be stricter. The check and write must be atomic; checking in the API and writing later recreates the race.

Fencing has an important limit: it rejects old work **after the protected resource has observed a newer epoch**. If an old request reaches storage before the new holder installs its epoch, a simple maximum-seen-token check may still accept it. Installing the new epoch before the new holder performs protected work establishes that newer-owner boundary, but does not by itself reject every old request immediately at lease expiry. An immediate-expiry rejection guarantee needs stronger integration, such as checking current lease validity atomically at the effect boundary under explicit clock/authority assumptions. State the exact guarantee rather than treating the token as magic.

External services may not accept fencing tokens. An email provider cannot “unsend” an old holder's message because a new epoch exists. Use provider idempotency, a transactional state transition at a local authority, reconciliation, or a different workflow. A lock cannot manufacture an enforcement feature the downstream resource lacks.

## Acquisition, renewal, release, and ownership

Acquisition must atomically establish absence/expiry and assign ownership. A separate read followed by write races with another acquirer. Renewal must check the exact current ownership identity and follow the authority's expiration rules; an expired holder must not accidentally renew a replacement's lease. Release must be compare-and-delete, not unconditional deletion by resource name.

For a Redis single-instance lease, `SET key token NX PX ttl` is a common acquisition building block. Release requires an atomic comparison with the stored token. Asynchronous failover can lose the lock record and allow another acquisition, so this is not automatically a safe coordination authority for correctness-critical external effects. Redis's own [distributed-lock documentation](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/) discusses assumptions; evaluate them against the actual failure model.

Distinguish locks used for **efficiency** from locks used for **correctness**. Duplicate cache regeneration may be tolerable. Duplicate fund transfer is not. The acceptable design for one should not be copied blindly into the other.

## TTL and renewal are engineering budgets

A short TTL speeds takeover after a crash but increases false expiry during pauses, packet delays, or overload. A long TTL reduces renewal pressure and false expiry but slows recovery. Choose from measured pause/latency distributions, failure recovery goals, and the safety mechanism at the resource. No finite TTL prevents all pauses in an asynchronous model.

Renew well before expiry with margin for several attempts; randomize fleet-wide renewal timing to avoid bursts. Stop initiating protected work when renewal becomes uncertain, but assume in-flight work can still arrive. Bound work duration or split it into checkpointed operations. Record lease acquisition, renewal latency/failures, expiry, fencing rejections, and takeover duration.

Clocks complicate elapsed-time reasoning. The authority may use its clock for expiry; the client should use a suitable local monotonic clock for duration budgets and account for acquisition time and drift assumptions. Comparing absolute wall-clock timestamps across machines without bounded skew is unsafe. A client that pauses can miss its own cancellation deadline; fencing still matters.

## Partitions and authority availability

During a partition, A may reach the protected storage but not the lease authority, while B reaches the authority and storage. That is exactly the topology that makes stale-holder writes dangerous. A consensus-backed authority may refuse new grants without a majority, preserving its safety at the expense of availability. The protected resource must enforce the resulting epoch decisions consistently with its own replication model.

Leader election often uses leases to reduce repeated coordination, but safe leader behavior still needs epochs and downstream enforcement. A lease can improve liveness and efficiency; it is not a substitute for [consensus](consensus-and-leadership.md) when the authority itself must agree on ownership.

## When not to use a distributed lock

Prefer an atomic database update or unique constraint when the entire invariant fits inside one database. Prefer idempotent operations when duplicate attempts are acceptable. Prefer partitioning ownership by key when work can be independent. Use a lease when temporary coordination solves a real problem and the safety argument includes crashes, partitions, pauses, clocks, authority failover, and the protected resource.

## Exercises

1. **Predict:** A resumes after expiry but before storage sees B's new fence. What does maximum-seen fencing alone permit?
2. **Debug:** A releases a lock using `DEL key` after its lease expired and B acquired it. What happens, and what atomic comparison fixes it?
3. **Implementation:** Simulate pause, expiry, takeover, and stale writes with a fake clock and a fenced resource. Assert accepted writes never regress below an observed epoch.
4. **Design:** Compare leases for cache filling, file publication, and sending money through an external provider.
5. **Interview:** Explain why fencing solves a problem expiration alone cannot, and name a boundary where fencing cannot be enforced.

<details><summary>Reasoning guide</summary>

The authority's ownership record and the resource's acceptance rule are separate state machines. The old write can arrive before the new fence is installed unless the design closes that gap. A random token proves acquisition identity; an ordered token lets the resource detect superseded authority. Both require atomic operations at their respective boundaries.

</details>

## Further reading and connections

[Kleppmann: how to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html), [etcd leases API](https://etcd.io/docs/v3.5/learning/api/#lease-api), and [Chubby paper](https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/). Connect to [clocks](logical-time.md), [quorums](replication-and-quorums.md), [idempotency](../20-production-patterns/idempotency-and-deduplication.md), and [rate-limit coordination](../13-reliability/rate-limiting.md).
