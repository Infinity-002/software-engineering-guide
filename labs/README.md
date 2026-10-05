# Runnable mechanism labs

These dependency-free Python 3.11+ models make three mechanisms executable. Run from the repository root:

```text
python labs/models.py
```

The tests exercise Bloom membership, token-bucket refill/bursts, and a stale lease holder against a fenced resource. They use deterministic inputs and a simulated clock; no network, database, credentials, or cloud account is needed. They are teaching models, not production libraries or proofs of a distributed implementation.

Read the code only after predicting these outcomes:

1. Every inserted Bloom key must be reported possibly present. Some absent keys may also be reported present. What changes as occupancy rises?
2. A bucket that refills five tokens/second cannot exceed its capacity after a long idle period. What does a backward clock observation do?
3. A lease can expire without stopping its holder's Python object from calling storage. After storage observes a higher fence, the old token is rejected. Before it observes that fence, a maximum-seen check alone can still accept old work.

After the tests pass, change one invariant at a time: clear a shared Bloom bit, remove atomic ownership checks in a concurrent adaptation, or accept every fence. Write the history that becomes unsafe. Do not interpret the single-process tests as evidence of thread safety, durable failover, or real clock bounds.

Continue with [Bloom filters](../11-system-data-structures/bloom-filters.md), [rate limiting](../13-reliability/rate-limiting.md), and [leases/fencing](../10-distributed-systems/leases-and-fencing.md). The [two-session PostgreSQL lab](postgres-concurrency.md) reproduces lost updates, optimistic conflicts, and write skew using a disposable database. The [projects](../projects/README.md) move these ideas into real application boundaries.
