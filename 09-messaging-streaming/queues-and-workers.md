# Queues, workers, and delivery semantics

Creating a Relay task should not wait for an email provider. A queue lets the request record durable work and a worker perform it later. This separates interactive latency from processing latency, but adds a new promise: accepted work must eventually succeed, expire, or become visibly failed.

## Queue, pub/sub, and stream answer different questions

A work queue distributes jobs among competing consumers. Pub/sub sends a publication to interested subscriptions, potentially with independent copies and durability policies. An event stream retains an ordered history within partitions for consumers to track independently. Products combine these models; name the required behavior instead of assuming a broker brand implies it.

A producer submits work to a broker. A consumer receives or reserves work, performs processing, and acknowledges according to the protocol. In RabbitMQ-style systems, exchanges route messages to queues through bindings, and consumers consume from queues. Publisher confirms concern broker acceptance under its durability configuration; consumer acknowledgements concern processing progress. They are separate boundaries, as the [RabbitMQ acknowledgement documentation](https://www.rabbitmq.com/docs/confirms) explains.

```text
API -> durable broker acceptance -> user gets operation ID
                 |
                 v
             worker receives
                 |
           durable business effect
                 |
             acknowledge
```

## The crash window determines delivery semantics

If a worker acknowledges before processing and then crashes, work can be lost: an at-most-once approach sacrifices retries. If it processes and then acknowledges, a crash between those steps can cause redelivery: an at-least-once approach requires duplicate tolerance. Neither order atomically coordinates an arbitrary external effect with the broker.

“Exactly once” must name its scope. A broker transaction may atomically consume and produce records within that broker ecosystem. It does not automatically make an email provider or bank execute once. Effectively-once business effects commonly require a durable unique operation identity and atomic state changes at the effect's authority. See [idempotency](../20-production-patterns/idempotency-and-deduplication.md) and [inbox](../20-production-patterns/outbox-inbox-and-sagas.md).

## Retries need classification and limits

Retry a transient connection failure with bounded exponential backoff and jitter. Do not endlessly retry a malformed payload or a permanently revoked permission. Track attempts and first-seen time, because ten attempts in one second and ten attempts over a day create different user experiences.

A **poison message** repeatedly fails because of its content or an unhandled deterministic condition. Requeueing it immediately can consume the whole worker fleet. A dead-letter queue (DLQ) isolates failed/expired work for inspection and controlled redrive. A DLQ is not a trash can: define ownership, alerts, retention, privacy controls, and replay policy. Fix the cause before redriving thousands of identical failures.

Visibility-timeout queues reserve work for a period; if processing exceeds it, another worker may receive the same job. Extend the reservation only while progress remains valid, and still make effects idempotent because renewal can fail. Other brokers use connection/channel lifecycle for redelivery. Know which failure detector your product uses.

## Ordering and backpressure

One queue does not always imply globally ordered effects. Multiple consumers, retries, prefetch, and variable processing times can reorder completion. If task updates must be applied in order, partition by task identity, use version checks, or design commutative operations. Global ordering reduces parallelism and creates a shared bottleneck.

Bound consumer prefetch and worker concurrency. Fetching 10,000 messages into one process may strand work behind a slow job and consume memory while other workers idle. Monitor oldest-message age, arrival rate, completion rate, retry rate, and in-flight work. Queue length alone cannot tell whether ten jobs are milliseconds or hours of work.

Backpressure can slow producers, delay batch submission, or reject new work. A durable queue absorbs bursts only up to storage and delay limits. If arrivals exceed service capacity indefinitely, the backlog grows indefinitely. Autoscaling should consider processing cost and downstream limits, not just queue depth.

## When not to add a broker

A database-backed job table can be enough for moderate work and has the advantage that business changes and job creation can share a transaction. A broker adds delivery features and throughput but also deployment, monitoring, compatibility, and recovery work. Use synchronous calls when the caller needs an immediate result and the dependency budget is acceptable; asynchronous communication changes the product workflow.

## Exercises

1. **Predict:** A worker commits its database change then crashes before acknowledgement. Draw the redelivery and show where deduplication must happen.
2. **Debug:** Queue depth falls but users still wait hours. Which metrics reveal reserved or repeatedly retried work?
3. **Implementation:** Build a worker with retry classification, bounded attempts, a DLQ, and graceful shutdown. Kill it at each boundary.
4. **Interview:** Explain why exactly-once delivery and exactly-once business effects are different claims.

<details><summary>Hints</summary>

The deduplication record and effect should share an atomic boundary where possible. If the effect is external, use that provider's idempotency/reconciliation support and retain unknown outcomes. Measure end-to-end job age and completion, not only broker dequeue counts.

</details>

## Further reading and connections

[RabbitMQ queues](https://www.rabbitmq.com/docs/queues), [Amazon SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html), and [Kafka delivery semantics](https://kafka.apache.org/41/design/design/). Continue to [Kafka](kafka-and-event-streams.md), [backpressure](../01-foundations/concurrency-and-io.md), and [reliability](../13-reliability/resilience-and-recovery.md).
