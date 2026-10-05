# Databases

**Prerequisites:** [Foundations](../01-foundations/README.md), [Backend and API engineering](../05-backend/README.md). **Roadmap level:** 2.

Read in this order; the checkpoint asks you to combine the ideas rather than repeat definitions.

Chapter | Priority | Concepts
--- | --- | ---
[Relational modeling and SQL](relational-model.md) | P0 | tables, rows, columns, primary keys, foreign keys, constraints, normalization, denormalization, joins, SQL
[Indexes and query execution](indexes-and-query-plans.md) | P0 | indexes, index lookup, range scans, composite indexes, prefix rules, covering indexes, selectivity, cardinality, clustered indexes, write amplification, query parsing, query planner, execution plans, sequential scans, index scans, join algorithms, statistics, EXPLAIN
[Transactions, isolation, and MVCC](transactions-and-mvcc.md) | P0 | ACID, atomicity, consistency, isolation, durability, transactions, locks, MVCC, dirty reads, non-repeatable reads, phantom reads, lost updates, isolation levels, database deadlocks, optimistic concurrency, pessimistic concurrency
[Pages, WAL, and crash recovery](storage-and-recovery.md) | P1 | pages, WAL, buffer pool, checkpoints, crash recovery, storage layout, vacuum, backup restoration
[Replication, partitioning, and data models](scaling-and-nosql.md) | P1 | read replicas, synchronous replication, asynchronous replication, replication lag, partitioning, sharding, resharding, hot partitions, distributed databases, key-value databases, document databases, wide-column databases, graph databases, search engines

## Checkpoint

Complete the [section checkpoint](CHECKPOINT.md) without opening the chapters, then revisit weak explanations.

[Roadmap](../ROADMAP.md) · [Progress](../PROGRESS.md) · [Exercises](../EXERCISES.md)
