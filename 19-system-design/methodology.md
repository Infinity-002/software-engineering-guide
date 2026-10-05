# A repeatable system design method

System design is the process of turning product requirements into explicit data, capacity, and failure contracts. Drawing a cache, queue, and database does not establish that they solve the problem. Start with the smallest design that satisfies the requirements, then break it with a concrete workload or failure.

## Fourteen decisions, in a useful order

1. **Clarify the product.** Who uses it, what action matters, and what is out of scope? “Chat” could mean a small private room or a million-person broadcast.
2. **List functional requirements.** Describe user-visible operations and workflows, including administration and deletion.
3. **List non-functional requirements.** State latency, durability, availability, freshness, privacy, and cost constraints. Name the measurement boundary.
4. **Estimate scale.** Derive average/peak traffic, storage, bandwidth, concurrency, and skew from explicit assumptions.
5. **Define APIs.** Include identity, pagination, asynchronous status, errors, and retry semantics.
6. **Design the data model.** Identify authoritative facts, keys, invariants, relationships, and retention.
7. **Draw the initial architecture.** Trace one write and one read through it. Mark synchronous versus asynchronous edges.
8. **Identify bottlenecks.** Ask which resource saturates first under the estimated workload.
9. **Scale selectively.** Add indexes, caches, replicas, partitions, queues, or independent services only for the identified limit.
10. **Analyze failures.** Crash between each pair of steps; delay/reorder/duplicate messages; remove a dependency; fill storage.
11. **Specify consistency.** Define what users can observe after writes, during partitions, and after recovery.
12. **Specify security.** Mark trust boundaries, authentication, resource authorization, abuse limits, and data lifecycle.
13. **Specify observability.** Choose SLIs and the logs/metrics/traces needed to distinguish likely failures.
14. **Defend trade-offs.** Explain what you rejected, what would change the decision, and how to evolve safely.

These steps are iterative. Discovering a cross-region latency constraint may change the API or product promise. Record assumptions as assumptions, not facts about a famous company's private architecture. The worked designs in this section are hypothetical services inspired by familiar products.

## Capacity math should change a decision

Suppose Relay has 200,000 daily active users, each making 40 reads and five writes. That is eight million reads/day and one million writes/day: about 93 reads/s and 12 writes/s averaged over 86,400 seconds. A tenfold peak gives roughly 930 reads/s and 120 writes/s. This is a starting workload hypothesis, not a reason by itself to shard.

At 1 KB per stored task change, one million changes/day is about 1 GB/day of logical payload, or 365 GB/year before indexes, replicas, WAL, metadata, and retained versions. If an attachment averages 5 MB, 100,000 uploads/day creates about 500 GB/day of original objects. Media can dominate storage and bandwidth even when API QPS is modest.

For stable averages, in-flight work is approximately throughput times latency. At 1,000 requests/s and 0.2 seconds average service time, expect about 200 in flight. If a dependency slows to two seconds, that becomes about 2,000 unless admission is bounded. This connects [Little's law](../01-foundations/concurrency-and-io.md) to overload design.

Use decimal or binary units explicitly. Separate logical data from replicated physical bytes, ingress from egress, and average from peak. State how skew changes the estimate: one celebrity, hot document, or large tenant can dominate a shard despite low global averages.

## Draw ownership, not just boxes

```text
Browser -> API -> PostgreSQL (authoritative task state + outbox)
                  |
                  v
              event relay -> queue -> notification worker -> provider
API -> Redis (disposable representation cache)
```

This diagram says where facts commit and which copies can be rebuilt. Ask when the user receives success, what survives each crash, and which operation identity crosses the queue/provider boundary. Draw separate control and data paths when bulk media or scheduler ownership would otherwise obscure the critical path.

## A failure table exposes hidden assumptions

| Boundary | Failure | Required response |
|---|---|---|
| Client to API | Response lost after commit | Retry/query by stable operation identity |
| API to database | Pool exhausted | Bounded wait and admission/shedding |
| Database to broker | Process crash between actions | Durable outbox intent |
| Worker to provider | Outcome unknown | Idempotent retry or reconciliation |
| Cache fill | Many concurrent misses | Coalescing and origin budget |
| Leader transfer | Old holder continues | Epoch/fencing at protected resource |

Do not add all these mechanisms automatically. Use the table to identify which guarantees the product actually needs. A best-effort analytics counter and a payment ledger deserve different failure handling.

## Interview and production versions

In an interview, spend a few minutes clarifying, then establish one coherent end-to-end path before deepening the hardest requirement. Narrate the trigger for each added component. If time is short, explicitly state the most important unresolved risk instead of adding unexplained boxes.

In production, replace assumptions with measurements and experiments. Include migration, cost, operational ownership, restore procedures, and rollout verification. A design is stronger when it predicts a failure you can reproduce and contains a plan to detect it.

## Exercises

1. **Design:** Apply all fourteen steps to Relay task creation at the workload above. Identify the first measurement you need before adding a cache.
2. **Predict:** Traffic remains constant while dependency latency grows tenfold. Estimate in-flight work and design a limit.
3. **Debug:** A proposed architecture has Kafka, Kubernetes, five databases, and no stated invariant. Rewrite it around one read and one write path.
4. **Interview:** Defend a single PostgreSQL-backed service for a moderate workload and state the evidence that would justify splitting it.

<details><summary>Review criteria</summary>

Every component has a requirement or measured bottleneck, every authoritative fact has an owner, and every acknowledged operation has a durability/recovery story. Estimates include units, peaks, skew, and confidence limits.

</details>

## Further reading and route

[Google SRE handling overload](https://sre.google/sre-book/handling-overload/), [AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html), and [Designing Data-Intensive Applications](https://dataintensive.net/) provide deeper foundations. Continue through [beginner](beginner-designs.md), [intermediate](intermediate-designs.md), and [advanced](advanced-designs.md) designs, then defend the [Relay evolution](../21-case-studies/relay-evolution.md).
