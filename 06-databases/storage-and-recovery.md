# Pages, WAL, and crash recovery

A database cannot synchronously rewrite every modified table and index page in an arbitrary order and still recover cleanly after a power loss. Storage engines separate the logical commit decision from the scheduling of bulk data-page writes.

## Pages and the buffer pool

Data is organized into fixed-size pages or blocks. A row lookup can require an index page followed by a table page. The buffer pool holds recently used pages in memory; the operating system may cache file data too. A dirty page has been modified in memory but is not yet persisted in its current form.

Page layout includes metadata and row/record locations, leaving room for updates and management. Large values may use out-of-line storage. Physical locality affects how many pages a scan touches. A query returning ten rows is not necessarily ten I/O operations: it may touch cached pages, many scattered pages, or a few densely packed ones.

## Write-ahead logging establishes recoverable order

The key rule is to persist the relevant log records before data pages containing those changes can be persisted. The log describes changes sufficiently for recovery under the engine's design. This turns scattered updates into a sequential logging path and lets data pages be written later. Commit acknowledgement depends on the configured log flush and replication policy; durability is not achieved merely because data reached an application buffer. PostgreSQL explains the ordering in [WAL introduction](https://www.postgresql.org/docs/current/wal-intro.html).

```text
transaction modifies pages in memory
          |
          v
append WAL records -> flush required WAL -> acknowledge durable commit
          |
          +-> dirty data pages written later
```

Group commit can amortize a durable flush across several transactions, trading small waiting intervals for throughput. Disabling durable flush behavior may improve a benchmark while weakening the promised failure contract. The setting is a product decision, not a free optimization.

## Checkpoints bound recovery work

A checkpoint coordinates persistence so recovery has a known starting region rather than replaying the entire historical log. Engines spread checkpoint work to avoid huge bursts, but aggressive settings can still cause I/O spikes. A checkpoint is not a backup and does not mean all future acknowledged work is safe without its later log.

After a crash, the engine examines durable state and replays required log records. The exact redo/undo and transaction-visibility mechanisms vary by engine. In PostgreSQL, WAL redo and transaction status/MVCC determine recoverable visible state; do not assume every database uses identical undo structures. Torn page writes and storage ordering are why engines have checksums, full-page logging strategies, and documented filesystem assumptions.

## MVCC cleanup is part of performance

Updates can leave old tuple versions. Vacuum makes dead versions reusable and performs other maintenance; it does not generally return every freed byte to the operating system. A growing file can contain reusable space. Long transactions, replication slots, and lagging consumers can retain versions or WAL and cause storage pressure through different mechanisms.

Monitor age and retention, not just current query throughput. A forgotten replication slot can retain large WAL volume even when application tables look stable. An idle transaction can impede cleanup while consuming little CPU. Both are ownership/lifecycle bugs.

## Backups, replicas, and recovery drills

A replica can faithfully copy an accidental deletion. It is a redundancy mechanism, not a complete backup strategy. A physical backup plus retained WAL can support point-in-time recovery within the available history; logical backups provide another portability and recovery trade-off. Consistency of the backup matters: copying live database files without the required backup procedure may not yield a usable image.

Define how far back recovery can go, which encryption keys and credentials are needed, and where restored clients will connect. Test restoration into an isolated environment, check business invariants, and measure the full time to usable service. “Backup job succeeded” is weaker evidence than “restore drill produced a verified system.” See [RPO/RTO](../13-reliability/resilience-and-recovery.md).

## Why not keep everything in RAM?

Memory is fast but finite and usually volatile. Even memory-oriented databases need persistence and replication policies when data loss matters. A larger buffer pool can help a read working set; it cannot repair a missing index, an unbounded transaction, or a durability contract that was never defined. Storage tuning should follow measured cache misses, write pressure, checkpoint activity, and latency.

## Exercises

1. **Predict:** The commit record is durable but the changed table page is not. Why can recovery still preserve the transaction?
2. **Debug:** Disk usage grows rapidly while table row counts stay constant. Distinguish dead tuples, indexes, retained WAL, and temporary spill files.
3. **Implementation:** In a disposable database, take a supported backup and restore it. Verify row counts and relational constraints, not just startup.
4. **Interview:** Explain why a checkpoint, a replica, and a backup solve different problems.

<details><summary>Hints</summary>

The durable log carries the information needed for replay. Retention can grow outside table files. Recovery evidence should include application-level checks and a measured time to service, including configuration and routing.

</details>

## Further reading and connections

[PostgreSQL database file layout](https://www.postgresql.org/docs/current/storage-file-layout.html), [continuous archiving](https://www.postgresql.org/docs/current/continuous-archiving.html), and [WAL configuration](https://www.postgresql.org/docs/current/wal-configuration.html). Connect to [LSM trees](../11-system-data-structures/lsm-trees.md) and [transactions](transactions-and-mvcc.md).
