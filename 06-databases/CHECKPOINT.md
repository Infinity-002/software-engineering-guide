# Checkpoint: Databases

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A query slows from 20 ms to three seconds at 50 million rows. Two concurrent transactions violate an on-call invariant, and a new task disappears briefly after refresh.

## Questions

1. Inspect actual plans, estimates, statistics, buffers, locks, and pool wait before choosing an index.
2. Explain B+ tree locality, composite key order, covering access, and write amplification.
3. Draw lost-update and write-skew histories; compare atomic updates, locks, version checks, and Serializable retry.
4. Explain MVCC cleanup, WAL-before-page ordering, checkpoints, and restore verification.
5. Diagnose replica lag and choose a read-your-writes policy before proposing sharding.

## Evidence to produce

Run two SQL sessions to reproduce a conflict, capture an EXPLAIN plan, and restore a small backup into an isolated database.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

The answer separates query cost, concurrency correctness, durability, and replica visibility. It states PostgreSQL-specific isolation behavior accurately and treats indexes/replicas as workload trade-offs.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
