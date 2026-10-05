# CQRS and event sourcing

Relay's task editor needs strict validation and concurrency checks. Its dashboard needs denormalized counts and recent activity. Forcing both through one representation can make reads expensive or writes tangled. CQRS separates command and query models; event sourcing makes an event history the authority. Either can exist without the other.

## Pattern 1: CQRS

**Problem and naive solution.** One generic CRUD model serves every write invariant and every reporting query. As reporting grows, complex joins and duplicated application calculations make both paths harder to evolve.

**Mechanism.** Commands express intent and enforce invariants through a write model. Queries read a model shaped for presentation or analysis. Separation can be conceptual inside one process and database; it does not require separate services or asynchronous replication. Introduce an independent read store only when workload or ownership justifies it.

**Example.** `CompleteTask(taskId, expectedVersion)` validates membership and state. A workspace dashboard reads a projection containing counts and the latest activity. An outbox event updates that projection asynchronously. The mutation response can return the authoritative new version while the dashboard advertises or tolerates lag.

**Failure modes.** Projection consumers fall behind, duplicate events, or apply events out of order. Users see a successful command but an old query result. A query model accidentally becomes writable, creating two authorities. Rebuilds can overload the source or expose incomplete data if switched into service too early.

**Trade-offs and use.** CQRS can simplify independently complex read/write models and scale their workloads differently, but adds synchronization and operational state. Define projection lag, repair, and read-your-writes behavior. Avoid it for simple CRUD where one well-indexed schema is clear and sufficient.

## Pattern 2: event sourcing

**Problem and naive solution.** Only storing the latest task row loses the sequence of domain decisions needed to reconstruct how it reached that state. Adding ad hoc logs may omit essential facts or disagree with the row.

**Mechanism.** Persist an ordered sequence of domain events as the authoritative history. Rebuild state by folding events through deterministic transition logic. A command loads/reconstructs the current aggregate, validates intent, and appends events conditionally on the expected stream version. The append must atomically reject conflicting concurrent versions.

```text
TaskCreated(title="Draft")
TaskRenamed(title="Review")
TaskAssigned(user=17)
TaskCompleted()
          |
          v
fold events -> current task state
```

Events record facts that happened, not merely incoming commands that may have been rejected. External nondeterministic results needed for replay must be recorded. Replaying `ChargeCard` as an instruction would charge again; replaying `PaymentAuthorized(providerId=...)` as a fact rebuilds state without repeating the effect.

**Example.** Relay can reconstruct task state at a historical stream position and build a new activity projection. Snapshots periodically store derived state plus the event position to shorten replay. They are an optimization; the system must define validation and fallback if a snapshot is missing or incompatible.

**Failure modes.** Old events outlive today's code. Renaming a field or changing its meaning can break replay. Use explicit event versions and upcasters/compatible readers, preserving original meaning. Bugs in historical transition code may require corrected projections or compensating events rather than editing history casually. Privacy erasure and retention become difficult when sensitive personal data is embedded immutably; design data minimization and separation up front.

**Trade-offs and use.** Event sourcing provides rich history and alternative projections but increases schema-evolution, replay, concurrency, and operational complexity. It is useful where business history and temporal reconstruction are central. Do not adopt it merely to get an audit log; a conventional database plus a transactional audit record often meets that need more simply.

## Ordering, replay, and the side-effect boundary

A projection can track `(streamId, version)` and reject gaps or duplicates according to policy. Global order across all aggregates is often unnecessary and costly. Decide whether cross-aggregate reporting tolerates asynchronous convergence. A new projection should rebuild alongside the old one, validate counts/invariants, catch up, and switch through a controlled versioned boundary.

Replay mode must be explicit for irreversible side effects. Notifications, provider calls, and webhooks should use durable effect identities or be disabled/reconciled under a separate replay contract. A historical event seen by a new consumer can be genuinely new work for that consumer, so “dedup everything forever” is also too vague.

## Exercises

1. **Check:** Give a CQRS design without event sourcing and an event-sourced design without a separate read database.
2. **Implementation:** Fold a task event stream, add an expected-version append check, and rebuild a projection twice to prove stable results.
3. **Debug:** A replay sends thousands of old emails. Identify the missing effect boundary and recovery controls.
4. **Design:** Evolve a historical event whose `amount` field lacked currency. Explain why a default may falsify history.
5. **Interview:** When is a transactional audit table preferable to event sourcing?

<details><summary>Hints</summary>

CQRS separates models; event sourcing chooses authoritative representation. Replay must preserve historical semantics, and missing facts cannot be invented safely. Audit requirements alone do not imply every business aggregate needs an event stream.

</details>

## Further reading and connections

[Azure CQRS pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs), [Azure event sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing), and [EventStoreDB documentation](https://developers.eventstore.com/). Connect to [Kafka](../09-messaging-streaming/kafka-and-event-streams.md), [outbox](outbox-inbox-and-sagas.md), and [audit logs](data-lifecycle-and-tenancy.md).
