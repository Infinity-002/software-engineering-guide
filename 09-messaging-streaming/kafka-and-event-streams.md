# Kafka and partitioned event streams

Relay now has notification, search, analytics, and audit consumers. Deleting each event after one worker receives it would prevent the others from maintaining independent progress. A retained log lets multiple consumers read the same history at their own pace.

## A topic is divided into ordered partitions

A Kafka topic contains partitions. Each partition is an append-oriented log with offsets identifying positions. Ordering is defined within a partition, not across the whole topic. A record key commonly selects a partition, so events for the same task can share an ordered history if the partitioning policy remains consistent.

```text
topic: task-events
partition 0: [0][1][2][3]...
partition 1: [0][1][2]...
                 |
     notifications group: independent offsets
     search group:        independent offsets
     analytics group:     independent offsets
```

A consumer group divides partition work among its members. Under the usual group model, a partition is assigned to one active consumer in that group at a time; separate groups can independently consume the same partition. More consumers than partitions do not automatically add active parallelism for that topic. Processing within a consumer can add concurrency, but then preserving commit order and effect order becomes an application concern.

## Offset commit is a progress claim

Reading a record is not the same as safely finishing its effect. Commit the offset too early and a crash can skip work; commit after effect completion and a crash can repeat work. For concurrent processing, committing beyond an unfinished earlier offset can lose that work on recovery. Track a contiguous completed prefix or use an appropriate processing model.

Retention is independent of whether every consumer has finished. A consumer offline longer than retention may lose access to required history and need a snapshot/rebuild. Log compaction can retain useful latest-key state while removing older superseded records under its rules; it is not a promise to preserve every historical event forever.

## Brokers, leaders, and replication

Brokers store partitions. A partition has a leader and replicas under the cluster's configuration. Producer acknowledgements, replication factor, minimum in-sync replica policy, leader-election rules, and storage guarantees jointly determine which failures can lose accepted records. “Kafka is durable” is not a complete configuration description.

Producer idempotence can suppress certain duplicate records caused by producer retries. Transactions can atomically coordinate records and consumer offsets within supported Kafka workflows, with consumers configured to observe the intended isolation. These mechanisms do not encompass an arbitrary external database or payment provider. The [Kafka design documentation](https://kafka.apache.org/41/design/design/) defines the scope; application effects still need a clear atomic boundary.

## Rebalancing is an ownership transition

When group membership or assignments change, partitions may move between consumers. Work in progress must be completed, abandoned safely, or fenced from conflicting effects. Long processing pauses can make a consumer appear unresponsive and trigger reassignment while it is still running. A partition assignment is not permission to ignore stale-worker behavior at external resources.

Frequent rebalances can interrupt progress. Inspect processing duration, poll behavior, membership churn, and deployment patterns. Graceful shutdown reduces avoidable churn but does not eliminate crash handling. Use [leases and fencing](../10-distributed-systems/leases-and-fencing.md) as a model for stale authority when processing correctness depends on exclusive ownership.

## Event contracts outlive code deployments

An event is a fact with identity, time/context, schema, and business meaning. Distinguish event occurrence time from ingestion/processing time. Late arrivals affect windows and analytics. Include stable identifiers and versions where consumers need deduplication or concurrency checks.

Schema evolution must support retained historical records and mixed consumer versions. Add fields compatibly, define defaults carefully, and avoid changing units or semantics under an old field name. A schema registry checks configured structural rules, not the truth of business meaning. Reprocessing old events can resend notifications unless replay behavior is designed separately from live side effects.

## Why not Kafka for every message?

Kafka is useful for retained event histories, high-throughput pipelines, and independent consumers. A small delayed email job system may be simpler with a work queue or database jobs. Partition planning, retention, rebalances, and consumer correctness are real costs. Choose replay and ordering requirements before choosing a stream platform.

## Exercises

1. **Predict:** A topic has six partitions and ten consumers in one group. How much partition-level concurrency can the group use?
2. **Debug:** Offset 12 is committed while record 10 is still processing. What happens if the process crashes?
3. **Design:** Partition Relay events for search and analytics. Explain hot-workspace behavior and a partition-count change.
4. **Implementation:** Replay a retained stream into a fresh projection without sending duplicate external notifications.
5. **Interview:** State a precise exactly-once claim and one effect outside its scope.

<details><summary>Hints</summary>

Commit progress must not skip unfinished work. Changing partition count can change key placement and complicate ordering across the transition. Separate replayable state projection from irreversible side effects and maintain durable operation identities.

</details>

## Further reading and connections

[Kafka introduction](https://kafka.apache.org/intro), [Kafka configuration](https://kafka.apache.org/41/configuration/), and [Confluent schema evolution](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html). Continue to [outbox](../20-production-patterns/outbox-inbox-and-sagas.md), [CQRS](../20-production-patterns/cqrs-and-event-sourcing.md), and [logical time](../10-distributed-systems/logical-time.md).
