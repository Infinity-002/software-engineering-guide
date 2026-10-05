# Outbox, inbox, sagas, and distributed transactions

Relay must create a task and reliably notify downstream services. A database transaction protects the task row, but a broker is a separate authority. This chapter follows the failure windows instead of assuming two successful-looking API calls form one transaction.

## Pattern 1: transactional outbox

**Problem.** A committed task must eventually produce an event. **Naive solution:** commit SQL, then publish. A crash between them loses the event. Publishing first is no better: a later SQL rollback leaves a fictional event.

**Mechanism.** Insert the task and an outbox row in the same database transaction. A relay polls committed rows or reads a change stream and publishes events. It records progress only after broker acceptance under the intended contract. The transaction makes the business fact and intent to publish atomic; publication itself is asynchronous.

```sql
BEGIN;
INSERT INTO tasks (workspace_id, title, status)
VALUES ($1, $2, 'open') RETURNING id;
-- The application uses the returned id in the next parameterized statement.
INSERT INTO outbox (event_id, aggregate_id, event_type, payload)
VALUES ($3, $4, 'TaskCreated', $5::jsonb);
COMMIT;
```

This fragment assumes the outbox schema and supplied IDs are defined by the project. Do not execute the two inserts on different pooled connections.

**Failure modes.** The relay can publish and crash before marking the row sent, producing a duplicate. Multiple relay workers can reorder events unless claiming/partitioning preserves the required aggregate order. Outbox growth can fill the database if publishing stops. Payload/schema changes must remain readable by relays and consumers across deployments.

**Trade-offs and use.** Outbox adds a table/change-data-capture path, retention, relay monitoring, and delivery lag. Use it when losing an event after a business commit is unacceptable. For a best-effort analytics ping with explicitly acceptable loss, it may be unnecessary. Monitor oldest unpublished age, not just row count, and provide a repair/replay procedure.

## Pattern 2: transactional inbox

**Problem.** At-least-once events can repeat a local effect. **Naive solution:** acknowledge first or put event IDs in a process cache. The former loses effects on crash; the latter forgets across restart.

**Mechanism and example.** In one consumer database transaction, insert a unique `(consumer, event_id)` marker and update the search-projection metadata or account record. If the marker already committed, skip the local effect. Acknowledge the broker after commit. A crash before acknowledgement causes redelivery but no duplicate committed local effect.

**Failure modes.** If the “effect” is an external email, the inbox transaction alone does not cover it. Create a local outgoing operation/outbox and coordinate the provider separately. ID reuse, premature retention cleanup, and replay under a different consumer identity can change behavior.

**Trade-offs and use.** Inbox makes duplicate tolerance explicit and durable, at the cost of a write/index per identity. Use it for non-idempotent local effects or projection processing requiring proof of once-per-event application. Avoid it when a version-conditional upsert already provides the needed guarantee with less state, while still checking stale/out-of-order semantics.

## Pattern 3: saga

**Problem.** A workflow spans independently committed systems: reserve inventory, authorize payment, and create shipment. **Naive solution:** pretend one long function either completely succeeds or completely fails. A crash after two steps leaves durable partial work.

**Mechanism.** A saga records progress through local transactions and defines compensating actions for completed steps when later work fails. An orchestrator can explicitly command steps and track state; choreography lets services react to events, reducing one central workflow component but making the overall state harder to see.

Example: reserve stock, authorize payment, then confirm order. If payment fails, release the reservation. If confirmation becomes unknown after payment succeeds, reconcile before releasing/refunding blindly. Compensation is a new business action, not time travel: an email cannot be unsent, an exchange rate may change, and a shipment may already leave the warehouse.

**Failure modes.** Commands, results, and compensations can duplicate or arrive late. Compensation can fail and need retry/manual review. Concurrent sagas can observe intermediate state unless reservations and domain rules isolate it. A refund arriving before a delayed charge needs explicit state handling.

**Trade-offs and use.** Sagas provide eventual workflow completion/recovery without one cross-system lock, but expose intermediate states and require careful business semantics. Use them for long-running multi-service workflows with meaningful compensation. Do not split a transaction into a saga when one database can enforce the invariant simply.

## Pattern 4: distributed transactions and two-phase commit

**Problem.** Several transactional participants must make one atomic commit decision. **Naive solution:** ask each to commit independently and roll back those already committed if another fails. Committed external effects may not be reversible.

**Mechanism.** In two-phase commit, a coordinator asks participants to prepare, then durably decides commit or abort and communicates that decision. Prepared participants retain enough state and locks/resources to honor the eventual decision. This can provide atomic agreement across supported participants under its recovery assumptions.

**Failure modes.** A prepared participant may block awaiting a failed coordinator's decision. Network partitions and recovery complicate liveness. Long prepared transactions hold resources and interfere with unrelated work. Adding replication to the coordinator improves some availability but does not make all cross-participant failures disappear.

**Trade-offs and use.** Use distributed transactions when participants support them, atomicity is required, and operational costs are acceptable. Do not assume a normal HTTP API or email service can join a two-phase commit. Sagas trade atomic visibility for compensating business workflows; outbox solves a narrower local-commit-plus-event-intent problem. They are not interchangeable names for “reliable messaging.”

## Exercises

1. **Predict:** The outbox relay publishes and crashes before marking sent. What must the consumer tolerate?
2. **Implementation:** Add outbox/inbox tables to a local database and inject crashes before/after each commit and acknowledgement.
3. **Design:** Write saga states and compensations for attachment scanning plus a paid storage upgrade. Include unknown outcomes and manual intervention.
4. **Debug:** A database has long-lived prepared transactions and blocked writes. Explain the coordinator/recovery investigation.
5. **Interview:** Compare outbox, inbox, saga, and two-phase commit by atomic boundary and failure behavior.

<details><summary>Review criteria</summary>

Every durable transition has an owner, identity, retry policy, and recovery path. Compensation is domain-specific. Outbox guarantees a durable publication intent, while duplicate publication remains possible. Inbox only covers effects in its own transaction boundary.

</details>

## Further reading and connections

[Debezium outbox event router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html), [PostgreSQL two-phase transactions](https://www.postgresql.org/docs/current/two-phase.html), and [Azure saga pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga). Connect to [idempotency](idempotency-and-deduplication.md), [transactions](../06-databases/transactions-and-mvcc.md), and [payment design](../19-system-design/advanced-designs.md).
