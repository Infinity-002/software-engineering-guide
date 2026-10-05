# Idempotency keys and deduplication

A user submits a payment, sees a timeout, and presses Retry. The server may already have completed the operation. Reliable APIs need a way to recognize repeated attempts at the same intent without confusing them with a genuinely new operation.

## Pattern 1: durable idempotency keys

**Problem and naive solution.** Disabling the submit button or remembering recent requests in an API process seems to prevent duplicates. It fails across tabs, retries, process restarts, and multiple replicas. Checking a table for a key and later inserting it also races unless the database arbitrates uniqueness atomically.

**Mechanism.** The caller generates a stable key for one logical operation and reuses it on retries. The server scopes it by principal/tenant and operation, stores a request fingerprint, and atomically coordinates the key with the business effect. The same key with different meaningful input is a conflict, not permission to return an unrelated old result.

For a purely local database effect, a transaction can claim the key, perform the change, and store the replayable result together:

```text
transaction (pseudocode)
  insert unique (tenant, operation, key, fingerprint)
  if conflict:
      compare fingerprint
      return stored completed result, or defined pending response
  apply business change
  store response/status associated with key
  commit
```

Actual conflict handling must account for concurrent transactions and database visibility. A unique constraint is the serialization point; an application `if` statement is not. Avoid returning a stored response before verifying the current caller is allowed to access it. Retain only safe response fields.

**Example.** Relay creates one export record and returns its operation ID. If the response is lost, retrying with the same key returns that ID. A new export request uses a new key even if its parameters are identical. Payload equality is not always intent equality.

**Failure modes.** A separate durable “in progress” claim can remain stuck after a crash unless recovery owns it. Holding a database transaction open across a slow external call can exhaust pools without making the external action atomic. Deleting idempotency records too early permits an old retry to create another effect. Fingerprints based on unstable serialization or omitted significant fields can misclassify requests.

**Trade-offs and use.** The pattern costs storage, coordination, and retention policy but makes uncertain retries manageable. Choose retention from the maximum supported retry horizon and business risk. Use it for creations, payment attempts, exports, and other repeatable client intents. Do not require it for every safe read or use it as a substitute for authorization and ordinary domain uniqueness.

## External effects require an outcome state machine

An external payment provider is outside the local database transaction. Persist an operation identity and use the provider's idempotency mechanism if available. Track states such as `pending`, `submitted`, `succeeded`, `failed`, and `unknown`, with clear transitions and reconciliation. A timeout after provider submission belongs in unknown/pending investigation, not automatic failure.

If the provider offers neither idempotency nor queryable operation identity, a local lock cannot guarantee one external effect across crashes. The product must accept a weaker guarantee, add manual reconciliation, or choose a provider/workflow with the required capability. “Exactly once” must stop at the actual atomic boundary.

## Pattern 2: message deduplication

**Problem and naive solution.** A consumer sees duplicate events and keeps their IDs in an in-memory set. A restart forgets the set; separate consumers maintain different sets; marking an event processed before the effect can lose work after a crash.

**Mechanism and example.** Use a stable event/operation ID and a durable uniqueness record at the effect authority. Insert the processed-event identity and update the local projection in one transaction. A conflicting identity means the same effect was already committed, so acknowledge without repeating it. This is the [inbox pattern](outbox-inbox-and-sagas.md) when organized as a consumer transaction boundary.

**Failure modes.** Different IDs for the same logical event bypass deduplication. Reused IDs for distinct events suppress valid work. Retention that expires before broker redelivery/replay allows repetition. Deduplicating all identical payloads can drop legitimate repeated actions, such as two intentional transfers of the same amount.

**Trade-offs and use.** A durable deduplication index consumes space and write throughput. Scope uniqueness to the right consumer/effect because separate consumers may each need to act once. Use it when repeated delivery is expected and effects are not naturally idempotent. Do not add it when the operation itself safely sets an authoritative version and duplicate attempts are harmless, unless audit/efficiency requires tracking.

## Natural idempotence still needs ordering

`set title = 'A'` is idempotent under repetition, but a delayed retry after `set title = 'B'` can revert newer intent. Combine operation identity with entity versions or ordering where required. Similarly, `increment count` is not idempotent, while “record event X's contribution once” can be made so with uniqueness.

Observe duplicate rate, fingerprint conflicts, pending-operation age, provider reconciliation failures, and replay outcomes. Never log raw sensitive payloads merely to debug fingerprints; use safe hashes and controlled records.

## Exercises

1. **Predict:** Two simultaneous requests use the same key and different amounts. Define the exact response and persisted result.
2. **Implementation:** Create an idempotent database mutation, kill the process after commit before response, and retry. Prove one business row exists.
3. **Debug:** A payment timed out and the worker retries with a newly generated provider key. Explain the duplication risk.
4. **Design:** Choose retention for client keys, broker event IDs, and long-lived replay archives.
5. **Interview:** Explain why idempotence alone does not prevent a stale write from overwriting a newer one.

<details><summary>Review criteria</summary>

The design identifies intent, scope, fingerprint, atomic boundary, concurrent-request behavior, retention, and unknown-outcome recovery. It does not claim a local database transaction covers an external provider.

</details>

## Further reading and connections

[Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests), [AWS safe retries](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), and [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html). Connect to [queues](../09-messaging-streaming/queues-and-workers.md), [leases](../10-distributed-systems/leases-and-fencing.md), and [API methods](../05-backend/api-design.md).
