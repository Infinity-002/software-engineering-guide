# Project 3 — Background processing system

Add durable task-export and notification workflows with a queue, workers, retries, a DLQ, idempotency, and transactional outbox/inbox boundaries. The success criterion is correct recovery after crashes at inconvenient moments.

## Contract and state model

`POST /exports` accepts a workspace/filter snapshot policy and returns an operation ID. `GET /exports/{id}` reports pending/running/ready/failed/cancelled or an explicitly defined unknown state. A completed export references a verified object. Notifications use a provider fake that records operation IDs and can simulate success followed by a lost response.

Separate job identity, attempt identity, and effect identity. Retrying an attempt should preserve the business operation identity. Store payload schema version, creation time, attempts, next eligible time, last safe error, and result reference. Define maximum attempts and maximum job age independently.

## Milestones and architecture

```text
API transaction: export intent + outbox
  -> relay -> queue -> worker -> database/object/provider effect
                  <- acknowledgement after defined durable boundary
```

First implement the job state machine with a real database. Then add a broker or a database-backed queue with explicit reservation semantics. Add an outbox relay so a committed export cannot lose its dispatch intent. Add inbox/deduplication for local effects and provider idempotency/reconciliation for external ones.

Introduce retry classification: transient network failure, provider throttling, permanent validation failure, and poison payload. Backoff with jitter, cap concurrency/prefetch, and route exhausted/permanent failures to a monitored DLQ. A redrive command should select a bounded set and preserve identity, with an audit of why it was retried.

## Crash matrix

Boundary | Expected behavior
--- | ---
Before API commit | No visible accepted export or outbox event
After commit, before publish | Relay eventually finds durable intent
After publish, before marking sent | Duplicate delivery tolerated
After worker claim, before effect | Redelivery/recovery after reservation failure
After local effect commit, before ack | Inbox/identity prevents repeated local effect
After provider success, before response | Unknown outcome reconciled with stable provider identity
During final object publication | Partial output remains unpublished and is cleaned/retried

Run each experiment deliberately using a disposable environment. A random process kill that misses the target window is not evidence that the window is safe.

## Observability and operation

Record job/attempt/trace identities without exposing sensitive payloads. Measure oldest eligible age, processing duration, attempts per completion, outbox age, DLQ age, and provider uncertainty. Graceful shutdown stops acquiring new work, drains within a bound, and remains safe if forced termination occurs.

Demonstrate backpressure by increasing arrival rate above worker capacity. The system must expose delay/rejection and remain within memory/storage policy. Autoscaling workers should respect PostgreSQL and provider limits.

## Acceptance criteria

- [ ] Every accepted job reaches a visible terminal state or a monitored recoverable pending/unknown state.
- [ ] Every crash-matrix row has a repeatable experiment and observed result.
- [ ] Duplicate local processing cannot apply the same business effect twice.
- [ ] Provider retries reuse stable identity and do not treat timeout as confirmed failure.
- [ ] Poison messages do not monopolize workers; DLQ inspection/redrive has ownership and bounds.
- [ ] Queue growth, outbox lag, and retries are observable, with defined retention/cleanup.
- [ ] Shutdown/restart preserves correctness and bounded resources.

## Exercises and review

Change the export schema while old messages remain queued. Show compatibility or a controlled migration/DLQ path. Replay a historical notification event without unintentionally resending external messages. Explain the precise scope of every “once” guarantee in your implementation.

<details><summary>Hints after implementation</summary>

The outbox relay can duplicate publication. An inbox only protects effects inside its database transaction. An external provider fake should support unknown outcomes, not merely success/failure, so the test exercises the real ambiguity.

</details>

## Further reading and connections

[Queues](../09-messaging-streaming/queues-and-workers.md), [outbox/inbox/sagas](../20-production-patterns/outbox-inbox-and-sagas.md), [idempotency](../20-production-patterns/idempotency-and-deduplication.md), and [reliability](../13-reliability/resilience-and-recovery.md). Use [RabbitMQ acknowledgements](https://www.rabbitmq.com/docs/confirms) or the chosen broker's equivalent primary documentation.
