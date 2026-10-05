# Rate limiting, fairness, and admission control

One Relay integration floods task creation and makes everyone else's requests slow. A rate limiter allocates a bounded share of arrival capacity to an identity. It must define the identity, cost unit, time model, burst policy, and behavior when its own state store fails.

## Algorithms encode different promises

A fixed window counts requests in each time bucket. It is cheap, but a client can send the full allowance just before a boundary and again just after it. A “100 per minute” fixed-window rule can allow almost 200 in a short interval around the boundary.

A sliding-window log stores timestamps and removes entries older than the window. It closely enforces the rolling count at the cost of memory proportional to recent requests. A sliding-window counter combines current and previous bucket counts with a time weight; it approximates the rolling total and can misestimate when arrivals are uneven within the prior bucket.

A token bucket accumulates tokens at rate `r` up to capacity `B`. A request costing `c` consumes `c` tokens if enough exist. This permits a burst up to the accumulated capacity while limiting sustained average usage. A leaky-bucket shaper drains queued work at a controlled rate, smoothing output; related policing formulations track virtual backlog rather than literally queueing. State which version you mean, and bound any real queue.

| Algorithm | State cost per key | Burst behavior | Main limitation |
|---|---|---|---|
| Fixed window | Constant | Boundary bursts | Coarse fairness |
| Sliding log | Recent request count | Exact rolling window under clock model | Memory and cleanup |
| Sliding counter | Constant | Approximate smoothing | Distribution assumptions |
| Token bucket | Constant | Explicit burst capacity | Atomic refill/consume needed |
| Leaky bucket | Constant meter or bounded queue | Smooth service/admission | Queue latency or rejection |

## Compare algorithms on one burst history

Suppose the policy says at most 100 requests in a rolling 60 seconds. A fixed window aligned to the clock accepts 100 at second 59.9 and another 100 at second 60.1. It obeys each fixed bucket but violates the intended rolling-window interpretation. The phrase “per minute” was ambiguous; the implementation did not choose the product contract for you.

A sliding log at time 60.1 removes timestamps at or before the chosen 0.1-second boundary, counts remaining entries, and atomically appends the new request only if the limit permits. The exact inequality at the cutoff should be documented and tested. A Redis sorted set can represent timestamps with unique request members; identical timestamp scores must not collapse distinct requests by reusing the same member. Removing old entries, counting, and adding must share one atomic decision.

A two-bucket sliding counter approximates the rolling count as `current + previous * (1 - elapsed/window)`. At 15 seconds into a 60-second bucket, it includes all current requests plus 75% of the previous bucket. This assumes the previous bucket's arrivals were distributed sufficiently evenly for the estimate to be useful. If they all arrived at its end, the approximation can undercount the true recent load. Use it only when that bounded/understood approximation fits the purpose.

Token buckets express a different contract: sustainable rate plus explicit burst capacity. With capacity 100 and refill 100/60 per second, a full bucket admits 100 immediately, then replenishes gradually. Over an interval of length `t`, the idealized envelope is at most about `B + r*t` admitted unit cost, subject to interval-boundary and starting-state details. It is not the same as a strict “100 in every possible 60-second interval” rule.

A queueing leaky bucket can instead spread departures at a fixed rate. That smooths a downstream provider's load but converts bursts into latency. At ten jobs/s, a backlog of 100 jobs adds roughly ten seconds before the tail begins service under a simple constant-cost model. Set a maximum backlog or age and reject/defer explicitly beyond it. A police-only leaky-bucket meter rejects excess rather than storing the actual jobs; be precise about which design you implement.

## Token-bucket mechanics

First imagine water refilling a bucket. Waiting longer creates permission to burst, but the bucket cannot exceed `B`. At time `now`, compute `elapsed = max(0, now-last)`, refill to `min(B, tokens + elapsed*r)`, then atomically test and deduct cost. Keep units consistent: seconds with tokens/second or milliseconds with tokens/millisecond.

```text
atomic operation (pseudocode)
  now = authority_time()
  refill = max(0, now - last) * rate
  available = min(capacity, tokens + refill)
  if available >= cost:
      tokens = available - cost
      allowed = true
  else:
      tokens = available
      allowed = false
  last = max(last, now)
  persist state and return allowed
```

Reject costs larger than capacity or define a special policy. Clock rollback handling prevents negative refill but does not solve arbitrary forward clock jumps; choose the time authority and failure assumptions. A process-local monotonic clock works for local limits, while a shared limiter needs consistent state/time semantics.

## Redis and atomicity

A naive Redis `GET`, local increment, `SET` loses updates under concurrent callers. Use an atomic script/function or transaction pattern appropriate to the algorithm. A fixed-window `INCR` followed separately by `EXPIRE` can leave a non-expiring key if the client crashes between commands; coordinate initialization/expiry atomically.

For a token bucket, reading state, refilling, deciding, and writing state must be one atomic operation at the authority. In Redis Cluster, multi-key atomic scripts have key-slot constraints. Failover can lose recently acknowledged limiter state depending on replication, allowing extra requests; decide whether this approximation is acceptable. A strict financial quota belongs in a stronger authoritative transaction, not an approximate abuse limiter.

## Distributed budgets and fairness

A central limiter gives a shared view but adds latency and an availability dependency. Local per-instance limits are fast but aggregate allowance grows with replica count. Leasing token batches to instances reduces coordination but permits bounded overshoot or temporarily stranded capacity. Name the bound and refill policy.

Key by the right principal: API key, authenticated tenant/user, route class, or source IP with care for shared NAT and proxies. Apply hierarchical limits where needed: global protection, per-tenant fairness, and expensive-operation budgets. Attackers can create many identities, so per-key limits alone may not protect the service. Avoid unbounded key cardinality from arbitrary input.

Return useful throttling information without promising an exact future success time. `429` and `Retry-After` can guide clients, but the next attempt can still face contention. Fail-open may preserve service during limiter outage but expose capacity; fail-closed protects a strict boundary but can turn the limiter into a system-wide outage. Choose per operation and retain a local emergency bound.

## Exercises

1. **Calculate:** A bucket has capacity 20, refills at 5/s, and is empty. How many unit requests can be accepted after three idle seconds? What about after ten?
2. **Implementation:** Build a deterministic token-bucket model with an injected clock. Test bursts, refill, backward time, and concurrent atomic decisions.
3. **Debug:** Doubling API replicas doubles a customer's effective allowance. Identify the hidden local-state assumption.
4. **Design:** Limit cheap reads, expensive exports, and tenant-wide paid quota with different mechanisms.
5. **Interview:** Contrast rate, concurrency, and queue-length limits during a dependency slowdown.

<details><summary>Hints</summary>

The bucket has 15 tokens after three seconds and 20 after ten. A rate bound does not cap concurrent work when duration grows. Paid quota may require durable exact accounting while abuse protection can tolerate a documented approximation.

</details>

## Further reading and connections

[Redis rate-limiter tutorial](https://redis.io/learn/develop/java/spring/rate-limiting/fixed-window), [Envoy rate limiting](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/other_features/global_rate_limiting), and [RFC 6585](https://www.rfc-editor.org/rfc/rfc6585). Connect to [backpressure](../01-foundations/concurrency-and-io.md), [atomic transactions](../06-databases/transactions-and-mvcc.md), and [rate-limiter design](../19-system-design/beginner-designs.md).
